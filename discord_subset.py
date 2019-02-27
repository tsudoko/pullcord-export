import markdown

class DiscordSubsetExtension(markdown.Extension):
	def extendMarkdown(self, md):
		"""Remove standard Markdown features not supported by Discord."""
		md.registerExtension(self)

		md.preprocessors.deregister("reference")

		md.parser.blockprocessors.deregister("indent")
		md.parser.blockprocessors.deregister("code")
		md.parser.blockprocessors.deregister("hashheader")
		md.parser.blockprocessors.deregister("setextheader")
		md.parser.blockprocessors.deregister("hr")
		md.parser.blockprocessors.deregister("olist")
		md.parser.blockprocessors.deregister("ulist")
		md.parser.blockprocessors.deregister("quote")

		md.inlinePatterns.deregister("reference")
		md.inlinePatterns.deregister("link")
		md.inlinePatterns.deregister("image_link")
		md.inlinePatterns.deregister("image_reference")
		md.inlinePatterns.deregister("short_reference")
		md.inlinePatterns.deregister("automail")
		md.inlinePatterns.deregister("linebreak")

def makeExtension(**kwargs):
	return DiscordSubsetExtension(**kwargs)
