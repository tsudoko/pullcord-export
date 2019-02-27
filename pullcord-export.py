#!/usr/bin/env python3
import collections
import datetime
import glob
import re
import sys

try:
	# python 3.7+
	datetime.datetime.fromisoformat
except AttributeError:
	# not fully correct, but good enough for this use case
	adjtz_re = re.compile(r"([-+][0-9]+):([0-9]+)")
	rmmil_re = re.compile(r"\..[0-9]*")
	class ___datetime(datetime.datetime):
		@staticmethod
		def fromisoformat(f):
			return datetime.datetime.strptime(adjtz_re.sub(r"\1\2", rmmil_re.sub("", f)), "%Y-%m-%dT%H:%M:%S%z")
	datetime.datetime = ___datetime
	del ___datetime

Entry = collections.namedtuple("Entry", ["timestamp", "dead", "type", "fields"])
Member = collections.namedtuple("Member", ["name", "discriminator", "avatar", "nick"])

def read_guild(f):
	g = {
		"guild": {},
		"channel": {},
		"member": {},
		"role": {},
		"emoji": {},
	}

	for l in f.readlines():
		ts, _, op, type, id, *rest = l.strip().split("\t")
		if type not in g:
			continue

		if id not in g[type]:
			g[type][id] = []

		if type == "member":
			name, discriminator, *rest = rest
			if rest:
				avatar, *rest = rest
			else:
				avatar = None
			if rest:
				nick, *rest = rest
			else:
				nick = None
			rest = Member(name, discriminator, avatar, nick)
		g[type][id].append(Entry(datetime.datetime.fromisoformat(ts), op != "add", type, rest))
	return g

class Message:
	def __init__(self, id, author):
		self.id = id
		self.author = author

		self.content = None
		self.editedtime = None
		self.deletedtime = None
		self.attachments = []
		self.embeds = []

	def __str__(self):
		return f"<Message {self.id} by {self.author} " + str([self.content, self.editedtime, self.deletedtime, self.attachments, self.embeds])

	def timestamp(self):
		return ((int(self.id) >> 22) + 1420070400000)/1000

member_re = re.compile("<@!?([0-9]+)>")
role_re = re.compile("<@&([0-9]+)>")
channel_re = re.compile("<#([0-9]+)>") # TODO
def mention(guild, date, msg):
	def member_name(m):
		id, *_ = m.groups()
		member = close_to(guild["member"][id], date).fields
		return "@" + (member.nick or member.name)

	def role_name(m):
		id, *_ = m.groups()
		role = close_to(guild["role"][id], date).fields
		return "@" + role[0]
	msg = member_re.sub(member_name, msg)
	msg = role_re.sub(role_name, msg)
	return msg

def unescape_msg(msg):
	return msg.replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\")

def read_channel(f):
	msgs = collections.OrderedDict()
	attachbuf = (None, [])
	reactbuf = (None, [])
	for l in f.readlines():
		ts, _, op, type, id, *rest = l.strip().split("\t")
		if type == "message":
			if op == "del":
				if id in msgs:
					del msgs[id] # TODO: show deletions
				continue
			authorid, *rest = rest
			msgs[id] = Message(id, authorid)
			if attachbuf[0] == id:
				msgs[id].attachments = attachbuf[1]
				attachbuf = (None, [])
			if reactbuf[0] == id:
				msgs[id].reactions = reactbuf[1]
				reactbuf = (None, [])
			if rest:
				editedtime, tts, content, *_ = rest
				msgs[id].editedtime = editedtime if editedtime else None
				msgs[id].content = unescape_msg(content)
		elif type == "attachment":
			msgid, *_ = rest
			if msgid in msgs:
				msgs[msgid].attachments.append(id)
			else:
				if attachbuf[0] is None:
					attachbuf = (msgid, [])
				elif attachbuf[0] != msgid:
					raise Exception(f"attachbuf id mismatch ({attachbuf[0]} != {msgid})")
				attachbuf[1].append(id)
		elif type == "reaction":
			...
	return msgs


def close_to(versions, dt):
	ret = versions[0]
	for v in versions[1:]:
		if v.timestamp >= dt:
			break
		ret = v
	return ret


def print_text(guild, cid, msgs):
	for _, m in msgs.items():
		date = datetime.datetime.fromtimestamp(m.timestamp(), datetime.timezone.utc)
		author = close_to(guild["member"][m.author], date).fields
		print(f"[{date.strftime('%Y-%m-%d %H:%M:%S')}] {author.nick or author.name}: ", end="")
		if m.content:
			print(mention(guild, date, m.content), end=" ")

		if m.attachments:
			for a in m.attachments:
				path = f"attachments/{cid}/{a}/"
				path = glob.glob(f"{path}/*")[0]
				url = "https://cdn.discordapp.com/" + path
				# TODO: use attachment name from the log if present
				print(f"{url} ", end="")
		print()

if __name__ == "__main__":
	_, gid, cid, *_ = sys.argv
	with open(f"channels/{gid}/guild.tsv") as f:
		guild = read_guild(f)
	with open(f"channels/{gid}/{cid}.tsv") as f:
		msgs = read_channel(f)

	print_text(guild, cid, msgs)
