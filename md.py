import markdown
from markdown.preprocessors import \
	NormalizeWhitespace, HtmlBlockPreprocessor
from markdown.blockprocessors import \
	EmptyBlockProcessor, CodeBlockProcessor, ParagraphProcessor
from markdown.inlinepatterns import \
	BacktickInlineProcessor, BACKTICK_RE, \
	EscapeInlineProcessor, ESCAPE_RE, \
	AutolinkInlineProcessor, AUTOLINK_RE, \
	HtmlInlineProcessor, HTML_RE, ENTITY_RE, \
	SimpleTextInlineProcessor, NOT_STRONG_RE, \
	DoubleTagInlineProcessor, EM_STRONG_RE, STRONG_EM_RE, \
	SimpleTagInlineProcessor, STRONG_RE, EMPHASIS_RE, SMART_STRONG_RE, SMART_EMPHASIS_RE


def build_preprocessors(md, **kwargs):
	r = markdown.util.Registry()
	r.register(NormalizeWhitespace(md), 'normalize_whitespace', 30)
	r.register(HtmlBlockPreprocessor(md), 'html_block', 20)
	return r


def build_block_parser(md, **kwargs):
	p = markdown.blockparser.BlockParser(md)
	p.blockprocessors.register(EmptyBlockProcessor(p), 'empty', 100)
	p.blockprocessors.register(CodeBlockProcessor(p), 'code', 80)
	p.blockprocessors.register(ParagraphProcessor(p), 'paragraph', 10)
	return p


def build_inlinepatterns(md, **kwargs):
	r = markdown.util.Registry()
	r.register(BacktickInlineProcessor(BACKTICK_RE), 'backtick', 190)
	r.register(EscapeInlineProcessor(ESCAPE_RE, md), 'escape', 180)
	r.register(AutolinkInlineProcessor(AUTOLINK_RE, md), 'autolink', 120)
	r.register(HtmlInlineProcessor(HTML_RE, md), 'html', 90)
	r.register(HtmlInlineProcessor(ENTITY_RE, md), 'entity', 80)
	r.register(SimpleTextInlineProcessor(NOT_STRONG_RE), 'not_strong', 70)
	r.register(DoubleTagInlineProcessor(EM_STRONG_RE, 'strong,em'), 'em_strong', 60)
	r.register(DoubleTagInlineProcessor(STRONG_EM_RE, 'em,strong'), 'strong_em', 50)
	r.register(SimpleTagInlineProcessor(STRONG_RE, 'strong'), 'strong', 40)
	r.register(SimpleTagInlineProcessor(EMPHASIS_RE, 'em'), 'emphasis', 30)
	r.register(SimpleTagInlineProcessor(SMART_STRONG_RE, 'strong'), 'strong2', 20)
	r.register(SimpleTagInlineProcessor(SMART_EMPHASIS_RE, 'em'), 'emphasis2', 10)
	return r


class Markdown(markdown.Markdown):
	def build_parser(self):
		self.preprocessors = build_preprocessors(self)
		self.parser = build_block_parser(self)
		self.inlinePatterns = build_inlinepatterns(self)
		self.treeprocessors = markdown.treeprocessors.build_treeprocessors(self)
		self.postprocessors = markdown.postprocessors.build_postprocessors(self)
