import React, { Component } from "react";

import { MarkdownBlock } from "./types";
import {LoadedBlockGlossProps, getGlossJson, getPreParts, parseGlossSpec, LoadedBlockGloss} from "./Gloss";
import {renderMarkdownBlock} from "./markdown";

type Props = {
  blocks: MarkdownBlock[],
}

type CachedBlock = {
  block: MarkdownBlock,
  data?: LoadedBlockGlossProps,
}

type State = {
  simple: boolean,
  seed: number,
  cachedBlocks: CachedBlock[],
}

export default class Document extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      simple: true,
      seed: 0,
      cachedBlocks: props.blocks.map(block => ({block})),
    }
  }

  componentDidMount() {
    this.state.cachedBlocks.forEach(cb => {
      if (cb.block.type == "CodeFence") {
        const {language, rows} = parseGlossSpec(cb.block.language);
        const {outline, translation} = getPreParts(cb.block);

        getGlossJson({language, outline}).then(res => {
          cb.data = {
            rows,
            translation,
            outline,
            language,
            errorMessage: (res.success ? undefined : res.message),
            content: (res.success ? res.response : undefined),
          }
          this.refresh();
        });
      }
    })
  }

  refresh() {
    this.setState({seed: this.state.seed + 1});
  }

  render() {
    const content = (this.state.simple) ? this.renderSimple() : this.renderBlocks();

    return (
      <>
        {this.renderSwitch()}
        {content}
      </>
    );
  }

  renderSwitch() {
    const button = (simple: boolean, label: string) => {
      return (
        <div className="col-6 go-down">
          <div className={this.state.simple === simple ? "selected" : ""}
            onClick={() => this.setState({simple})}>
            <h3>{label}</h3>
          </div>
        </div>
      );
    }

    return (
      <div className="row">
        {button(true, "Simplified")}
        {button(false, "Analysis")}
      </div>
    );
  }

  renderSimple() {
    const datas = this.state.cachedBlocks
      .filter(cb => cb.block.type === "CodeFence")
      .map(cb => cb.data)

    const romanization = datas.map(d => d?.content?.romanization.join(" ") || "")
      .reduce((prev, curr) => prev + " " + curr, "");

    const falavay = datas.map(d => d?.content?.falavay.join("\u200b") || "")
      .reduce((prev, curr) => prev + (prev && ".\u200b") + curr, "")

    const translation = datas.map(d => d?.translation || "")
      .reduce((prev, curr) => prev + " " + curr, "")

    return (
      <>
        <p className="falavay">{falavay}</p>
        <p className="romanization">{romanization}</p>
        <p>{translation}</p>
      </>
    );
  }

  renderBlocks() {
    return this.state.cachedBlocks.map((cb, i) => {
      if (cb.block.type === "CodeFence") {
        if (cb.data === undefined) {
          return null;
        } else {
          return <LoadedBlockGloss {...cb.data} key={i}/>;
        }
      } else {
        return <div key={i}>{renderMarkdownBlock(cb.block)}</div>;
      }
    });
  }
}
