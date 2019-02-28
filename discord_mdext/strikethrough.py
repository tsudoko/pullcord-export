import markdown

class DiscordStrikethroughExtension(markdown.Extension):
	def extendMarkdown(self, md):
		md.registerExtension(self)
		md.inlinePatterns.register(markdown.inlinepatterns.SimpleTagInlineProcessor("(~~)(.*?)~~", "s"), "strike", 65)

def makeExtension(**kwargs):
        return DiscordStrikethroughExtension(**kwargs)
