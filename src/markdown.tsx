import React, { Component } from "react";
import { Link } from "react-router-dom";

import {renderInlineCode, renderMarkdownPreformatted, extraFormatting} from "./Gloss";
import {
  InlineCode,
  MarkdownBlock,
  MarkdownHeading,
  MarkdownList,
  MarkdownParagraph, MarkdownTable,
  MistletoeDocument,
  ParagraphChild
} from "./types";

function ParagraphChild({e}: {e: ParagraphChild}) {
  switch (e.type) {
    case "LineBreak":
      return e.soft ? <>{' '}</> : <br/>;
    case "RawText":
      return <>{extraFormatting(e.content)}</>;
    case "Emphasis":
      return <i>
        {paragraphChildren(e.children)}
      </i>;
    case "Strong":
      return <b>
        {paragraphChildren(e.children)}
      </b>
    case "InlineCode":
      return renderInlineCode(e);
    case "Link":
      return <Link to={e.target}>
        {paragraphChildren(e.children)}
      </Link>;
    case "Image":
      return <div className={"image-inset"}>
        <img src={e.src}/>
        {paragraphChildren(e.children)}
      </div>
    default:
      console.log(e);
      throw `Unknown child type: ${e['type']}`;
  }
}

function paragraphChildren(children: ParagraphChild[]) {
  return children.map((c, i) => <ParagraphChild e={c} key={i}/>);
}

function MarkdownParagraph({para}: {para: MarkdownParagraph}) {
  return (
    <div className={"paragraph"}>
      {paragraphChildren(para.children)}
    </div>
  );
}

function renderMarkdownHeading(block: MarkdownHeading) {
  const children = paragraphChildren(block.children);

  switch (block.level) {
    case 1:
      return <h2>{children}</h2>;
    case 2:
      return <h3>{children}</h3>;
    default:
      return <h4>{children}</h4>;
  }
}

function renderMarkdownTable(block: MarkdownTable) {
  return (
    <table>
      <thead>
      <tr>
        {block.header.children.map((cell, i) => (
          <th key={i}>{paragraphChildren(cell.children)}</th>
        ))}
      </tr>
      </thead>
      <tbody>
      {block.children.map((row, i) => (
        <tr key={i}>
          {row.children.map((cell, j) => (
            <td key={j}>{paragraphChildren(cell.children)}</td>
          ))}
        </tr>
      ))}
      </tbody>
    </table>
  );
}

function renderMarkdownList(block: MarkdownList) {
  return <ul>{block.children.map((li, i) => (
    <li key={i} className="inline">{renderMarkdownBlock(li.children[0])}</li>
  ))}</ul>
}

export function renderMarkdownBlock(block: MarkdownBlock) {
  switch (block.type) {
    case "Paragraph":
      return <MarkdownParagraph para={block}/>;
    case "Table":
      return renderMarkdownTable(block);
    case "CodeFence":
      return renderMarkdownPreformatted(block);
    case "Heading":
      return renderMarkdownHeading(block);
    case "List":
      return renderMarkdownList(block);
    default:
      console.log(block);
      throw `Unknown block type: ${block['type']}`;
  }
}