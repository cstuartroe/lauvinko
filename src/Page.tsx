import React, { Component } from "react";
import { useParams } from 'react-router-dom';

import PageHeader  from "./PageHeader"
import SectionLinks from "./SectionLinks";
import { MistletoeDocument } from "./types";
import { renderMarkdownBlock } from "./markdown";
import Document from "./Document";
import PageManager from "./PageManager";

type Props = {
  name: string,
}

type State = {
  status: "pending" | "succeeded" | "failed",
  document?: MistletoeDocument,
}

class _Page extends Component<Props, State> {
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
      .then(() => {
        if ((new URL(window.location.href)).hash) {
          setTimeout(() => {window.location.href = window.location.href}, 500);
        }
      })
      .catch(_ => this.setState({
        status: "failed",
      }));
  }

  render() {
    return (
      <div>
        <PageHeader name={this.props.name} show_title={true}/>
        {this.renderContent()}
        <SectionLinks sections={PageManager.get(this.props.name)?.subsections || []}/>
        {this.state.document && this.state.document.children.length >= 4 && (
          <PageHeader name={this.props.name} show_title={false}/>
        )}
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
        if (this.state.document == undefined) {
          return null;
        }

        const blocks = this.state.document.children;

        if (blocks.length > 0 && blocks[0].type == "CodeFence") {
          return <Document blocks={blocks}/>;
        } else {
          return blocks.map((b, i) => (
            <div key={i}>{renderMarkdownBlock(b)}</div>
          ));
        }
    }
  }
}

function Page() {
  const { name } = useParams();

  if (name === undefined) {
    return null;
  }

  return <_Page name={name}/>
}

export default Page;