import React, { Component } from "react";
import { Link } from "react-router-dom";

import PageHeader  from "./PageHeader"
import SectionLinks from "./SectionLinks";
import {renderInlineCode, renderMarkdownPreformatted} from "./Gloss";
import {
  InlineCode,
  MarkdownBlock,
  MarkdownParagraph,
  MarkdownPreformatted,
  MarkdownTable,
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
      return <>{e.content}</>;
    case "Emphasis":
      return <i>
        {paragraphChildren(e.children)}
      </i>;
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

function MarkdownBlock({block}: {block: MarkdownBlock}) {
  switch (block.type) {
    case "Paragraph":
      return <MarkdownParagraph para={block}/>;
    case "Table":
      return null;
    case "CodeFence":
      return renderMarkdownPreformatted(block);
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