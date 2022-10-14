export type SectionDefinition = {
  name: string,
  title: string,
  subsections: string[],
  parent: null | string,
}

export type MistletoeDocument = {
  type: "Document",
  children: MarkdownBlock[],
}

export type MarkdownBlock = (
  MarkdownParagraph
  | MarkdownTable
  | MarkdownPreformatted
  | MarkdownHeading
  | MarkdownList);

export type MarkdownParagraph = {
  type: "Paragraph",
  children: ParagraphChild[],
}

export type ParagraphChild = RawText | InlineCode | Emphasis | Strong | Link | Image | LineBreak;

type RawText = {
  type: "RawText",
  content: string,
}

export type InlineCode = {
  type: "InlineCode",
  children: RawText[],
}

export type Emphasis = {
  type: "Emphasis",
  children: ParagraphChild[],
}

export type Strong = {
  type: "Strong",
  children: ParagraphChild[],
}

export type Link = {
  type: "Link",
  target: string,
  children: ParagraphChild[],
}

export type Image = {
  type: "Image",
  src: string,
  children: ParagraphChild[],
}

type LineBreak = {
  type: "LineBreak",
  soft: boolean,
}

export type MarkdownHeading = {
  type: "Heading",
  level: number,
  children: ParagraphChild[],
}

export type MarkdownTable = {
  type: "Table",
  header: TableRow,
  children: TableRow[],
}

type TableRow = {
  type: "TableRow",
  children: TableCell[],
}

type TableCell = {
  type: "TableCell",
  children: ParagraphChild[],
}

export type MarkdownPreformatted = {
  type: "CodeFence",
  language: string,
  children: RawText[],
}

export type MarkdownList = {
  type: "List",
  children: ListItem[],
}

type ListItem = {
  type: "ListItem",
  children: [MarkdownBlock],
}

export type ApiFailure = {
  success: false,
  message: string,
}

export type ApiSuccess<T> = {
  success: true,
  response: T,
}

export type ApiResponse<T> = ApiFailure | ApiSuccess<T>;
