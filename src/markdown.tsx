import React, { Component } from "react";
import { Link } from "react-router-dom";

import {renderInlineCode, renderMarkdownPreformatted, extraFormatting, CopyLink} from "./Gloss";
import {
  InlineCode,
  MarkdownBlock,
  MarkdownHeading,
  MarkdownList,
  MarkdownParagraph,
  MarkdownTable,
  MarkdownLink,
  ParagraphChild,
  TableRow,
} from "./types";
import PageManager from "./PageManager";

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
      return renderLink(e);
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

function snake_casify(s: string): string {
  let out = "";

  for (let i = 0; i < s.length; i++) {
    const c = s[i];

    if (' _'.includes(c)) {
      out += '_'
    } else if (c.match(/[a-zA-Z0-9]/g)) {
      out += c.toLowerCase()
    }
  }

  return out
}

function renderMarkdownHeading(block: MarkdownHeading) {
  const children = paragraphChildren(block.children);

  let id: string | undefined = undefined;
  if (block.children.length === 1 && block.children[0].type === "RawText") {
    id = snake_casify(block.children[0].content)
  }

  let copier = null;
  if (id) {
    const currentUrl = new URL(window.location.href);
    const target = `${currentUrl.protocol}//${currentUrl.host}${currentUrl.pathname}#${id}`;

    copier = <CopyLink link={target}/>;
  }

  switch (block.level) {
    case 1:
      return <h2 id={id}>{copier} {children}</h2>;
    case 2:
      return <h3 id={id}>{copier} {children}</h3>;
    default:
      return <h4 id={id}>{copier} {children}</h4>;
  }
}

function renderMarkdownRow(row: TableRow) {
  const children: React.ReactNode[] = [];
  let colspan: number = 1;

  row.children.forEach((cell, j) => {
    if (cell.children.length == 1 && cell.children[0].type == "RawText") {
      switch (cell.children[0].content) {
        case "+":
          colspan += 1;
          return;
        case "^":
          children.push(<td key={j} colSpan={1} style={{borderTop: "4px solid white"}}/>);
          return;
      }
    }

    children.push(
      <td key={j} colSpan={colspan} style={{textAlign: "center"}}>
        {paragraphChildren(cell.children)}
      </td>
    );
  });

  return children;
}

function renderMarkdownTable(block: MarkdownTable) {
  return (
    <table style={{marginBottom: "10px"}}>
      <thead>
      <tr>{renderMarkdownRow(block.header)}</tr>
      </thead>
      <tbody>
      {block.children.map((row, i) => (
        <tr key={i}>{renderMarkdownRow(row)}</tr>
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
    case "ThematicBreak":
      return <hr/>;
    default:
      console.log(block);
      throw `Unknown block type: ${block['type']}`;
  }
}

function renderLink(e: MarkdownLink) {
  if (e.children.length == 0) {
    return (
      <Link to={"/" + e.target}>
        {PageManager.get(e.target)?.title}
      </Link>
    );
  }

  if (e.target.startsWith("http")) {
    return (
      <a href={e.target} target="_blank">
        {paragraphChildren(e.children)}
      </a>
    );
  }

  return (
    <Link to={e.target}>
      {paragraphChildren(e.children)}
    </Link>
  );
}
