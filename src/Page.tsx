import React, { Component } from "react";
import { Link } from "react-router-dom";

import PageHeader  from "./PageHeader"
import SectionLinks from "./SectionLinks";
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
import PageManager from "./PageManager";

type Props = {
  name: string,
}

type State = {
  status: "pending" | "succeeded" | "failed",
  document?: MistletoeDocument,
}

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
    <li key={i} className="inline"><MarkdownBlock block={li.children[0]}/></li>
  ))}</ul>
}

function MarkdownBlock({block}: {block: MarkdownBlock}) {
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

class Page extends Component<Props, State> {
  constructor(props: Props) {
    super(props);

    this.state = {
      status: "pending",
    };
  }

  componentDidMount() {
    this.loadPage();
  }

  componentDidUpdate(prevProps: Readonly<Props>, prevState: Readonly<State>, snapshot?: any) {
    if (prevProps.name !== this.props.name) {
      this.loadPage();
    }
  }

  loadPage() {
    this.setState({
      status: "pending",
      document: undefined,
    });

    fetch('/page/' + this.props.name)
      .then(response => response.json())
      .then(doc => this.setState({
        document: doc as MistletoeDocument,
        status: "succeeded",
      }))
      .catch(_ => this.setState({
        status: "failed",
      }));
  }

  render() {
    return (
      <div>
        <PageHeader name={this.props.name}/>
        {this.renderContent()}
        <SectionLinks sections={PageManager.get(this.props.name)?.subsections || []}/>
      </div>
    );
  }

  renderContent() {
    switch (this.state.status) {
      case "pending":
        return null;
      case "failed":
        return  <p>There was a problem loading the page.</p>;
      case "succeeded":
        return this.state.document?.children.map((b, i) => (
          <MarkdownBlock block={b} key={i}/>
        ));
    }
  }
}

export default Page;