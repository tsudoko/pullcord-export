import html
import re

import markdown

class DiscordFencedCodeExtension(markdown.Extension):
	def extendMarkdown(self, md):
		md.registerExtension(self)
		md.preprocessors.register(DiscordFencedBlockPreprocessor(md), "fenced_code_block", 25)

class DiscordFencedBlockPreprocessor(markdown.preprocessors.Preprocessor):
	block_re = re.compile("```([-.+#a-zA-Z]\n)?(.*)```", flags=re.MULTILINE|re.DOTALL)
	html_template = "<pre><code{attrs}>{code}</code></pre>"
	def __init__(self, md):
		super().__init__(md)

	@classmethod
	def _sub(cls, m):
		attrs = ""
		lang, code = m.groups()
		if lang:
			attrs += f' class="{html.escape(lang)}"'
		return cls.html_template.format(attrs=attrs, code=html.escape(code))

	def run(self, lines):
		return self.block_re.sub(self._sub, '\n'.join(lines)).split("\n")

def makeExtension(**kwargs):
	return DiscordFencedCodeExtension(**kwargs)
