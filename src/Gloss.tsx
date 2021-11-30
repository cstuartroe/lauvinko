import React, { Component } from "react";
import {InlineCode, MarkdownPreformatted} from "./types";

type GlossRow = "analysis" | "transcription" | "falavay" | "ipa";

const ROW_ABBREVS: {[key: string]: GlossRow} = {
  a: "analysis",
  t: "transcription",
  f: "falavay",
  i: "ipa",
}

type Language = "lv" | "pk";

type GlossParams = {
  outline: string,
  language: Language,
}

export function splitOnce(s: string, separator: string): [string, string] {
  const i = s.indexOf(separator);

  if (i === -1) {
    return [s, ""];
  } else {
    return [s.slice(0, i), s.slice(i+1)];
  }
}

export function parseGlossSpec(spec: string): {language: Language, rows: GlossRow[]} {
  if (spec === "") {
    return {
      language: "lv",
      rows: ["falavay", "transcription", "analysis"],
    };
  } else if (spec.includes(';')) {
    const [language, row_abbrevs] = splitOnce(spec, ';');

    return {
      language: language as Language,
      rows: Array.from(row_abbrevs).map(a => ROW_ABBREVS[a]),
    };
  } else {
    return {
      language: spec as Language,
      rows: ["falavay", "transcription", "analysis"],
    };
  }
}

function getGlossJson(params: GlossParams): Promise<GlossResponse> {
  return fetch('/gloss?' + new URLSearchParams(params))
    .then(response => response.json());
}

type GlossResponse = {
  analysis: string[],
  transcription: string[],
  falavay: string[],
  ipa: string[],
}

type InlineGlossProps = GlossParams & {
  rows: GlossRow[],
}

type GlossState = {
  content?: GlossResponse
}

class InlineGloss extends Component<InlineGlossProps, GlossState> {
  constructor(props: InlineGlossProps) {
    super(props);

    this.state = {};
  }

  componentDidMount() {
    const { language, outline } = this.props;

    getGlossJson({language, outline}).then(gr => this.setState({content: gr}))
  }

  render() {
    return (
      <>
        {this.props.rows.map(row => this.renderRow(row))}
      </>
    );
  }

  renderRow(row: GlossRow) {
    if (this.state.content === undefined) {
      return null;
    }

    const {
      analysis,
      transcription,
      falavay,
      ipa,
    } = this.state.content;

    switch (row) {
      case "analysis":
        return <span className={"analysis"}>{analysis.join(' ')}</span>;
      case "transcription":
        return <span className={'transcription'}>{transcription.join(' ')}</span>;
      case "falavay":
        return <span className={'falavay'}>{falavay.join('')}</span>;
      case "ipa":
        return <span className={'ipa'}>{'[' + ipa.join(' ') + ']'}</span>;
    }
  }
}

function AugmentPair({outline}: {outline: string}) {
  const sharedProps: Omit<InlineGlossProps, "outline"> = {
    language: "lv",
    rows: ["falavay", "transcription"],
  };

  return (
      <span>
        <InlineGloss {...sharedProps} outline={outline + ".$au$"}/>
        {", "}
        <InlineGloss {...sharedProps} outline={outline + ".$na$"}/>
      </span>
  );
}

function renderInlineCode(code: InlineCode) {
  const source = code.children[0].content;

  const [rawSpec, outline] = splitOnce(source, ' ');

  if (rawSpec === "ap") {
    return <AugmentPair outline={outline}/>
  } else {
    const spec = parseGlossSpec(rawSpec);

    return <InlineGloss
      language={spec.language}
      outline={outline}
      rows={spec.rows}
    />
  }
}

type BlockGlossProps = GlossParams & {
  rows: GlossRow[],
  translation: string,
}

class BlockGloss extends Component<BlockGlossProps, GlossState> {
  constructor(props: BlockGlossProps) {
    super(props);

    this.state = {};
  }

  componentDidMount() {
    const { language, outline } = this.props;

    getGlossJson({language, outline}).then(gr => this.setState({content: gr}))
  }

  render() {
    return (
      <div className={"gloss"}>
        <table>
          <tbody>
            {this.props.rows.map(row => this.renderRow(row))}
            <tr>
              <td colSpan={this.state.content?.analysis.length || 1}>
                {'"' + this.props.translation + '"'}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    );
  }

  renderRow(row: GlossRow) {
    if (this.state.content === undefined) {
      return null;
    }

    const {
      analysis,
      transcription,
      falavay,
      ipa,
    } = this.state.content;

    switch (row) {
      case "analysis":
        return (
          <tr>
            {analysis.map((word, i) =>
              <td className={"analysis"} key={i}>{word}</td>
            )}
          </tr>
        );

      case "transcription":
        return (
          <tr>
            {transcription.map((word, i) =>
              <td className={'transcription'} key={i}>{word}</td>
            )}
          </tr>
        );

      case "falavay":
        return (
          <tr>
            {falavay.map((word, i) =>
              <td className="falavay" key={i}>{word}</td>
            )}
          </tr>
        );

      case "ipa":
        return (
          <tr>
            {ipa.map((word, i) =>
              <td className={'ipa'} key={i}>{word}</td>
            )}
          </tr>
        );
    }
  }
}

function renderMarkdownPreformatted(pre: MarkdownPreformatted) {
  const {language, rows} = parseGlossSpec(pre.language);

  const lines = pre.children[0].content.split("\n");

  return <BlockGloss outline={lines[0]} translation={lines[1]} {...{language, rows}}/>;
}

export {
  BlockGloss,
  InlineGloss,
  AugmentPair,
  renderInlineCode,
  renderMarkdownPreformatted,
};