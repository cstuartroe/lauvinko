import React, { Component } from "react";
import {InlineCode, MarkdownPreformatted} from "./types";

export type GlossRow = "analysis" | "romanization" | "falavay" | "narrow_transcription" | "broad_transcription";

const ROW_ABBREVS: {[key: string]: GlossRow} = {
  a: "analysis",
  r: "romanization",
  f: "falavay",
  n: "narrow_transcription",
  b: "broad_transcription",
}

const ROW_CLASSES: {[key in GlossRow]: string} = {
  analysis: "analysis",
  romanization: "romanization",
  falavay: "falavay",
  narrow_transcription: "ipa",
  broad_transcription: "ipa",
}

export type Language = "lv" | "pk";

export type GlossParams = {
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
      rows: ["falavay", "romanization", "analysis"],
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
      rows: ["falavay", "romanization", "analysis"],
    };
  }
}

export function getGlossJson(params: GlossParams): Promise<GlossResponse> {
  return fetch('/api/gloss?' + new URLSearchParams(params))
    .then(response => response.json());
}

export type GlossData = {
  analysis: string[],
  romanization: string[],
  falavay: string[],
  narrow_transcription: string[],
  broad_transcription: string[],
}

export type GlossResponse = {
  success: true,
  response: GlossData,
} | {
  success: false,
  message: string,
}

type InlineGlossProps = GlossParams & {
  rows: GlossRow[],
}

type GlossState = {
  content?: GlossData,
  errorMessage?: string,
}

class InlineGloss extends Component<InlineGlossProps, GlossState> {
  constructor(props: InlineGlossProps) {
    super(props);

    this.state = {};
  }

  componentDidMount() {
    const { language, outline } = this.props;

    getGlossJson({language, outline}).then(gr => {
      if (gr.success) {
        this.setState({content: gr.response});
      }
    });
  }

  render() {
    return (
      <>
        {this.props.rows.map((row, i) => this.renderRow(row, i))}
      </>
    );
  }

  renderRow(row: GlossRow, key: number) {
    if (this.state.content === undefined) {
      return null;
    }

    const {
      analysis,
      romanization,
      falavay,
      narrow_transcription,
      broad_transcription,
    } = this.state.content;

    const className = ROW_CLASSES[row];

    switch (row) {
      case "analysis":
        return <span className={className} key={key}>{analysis.join(' ')} </span>;
      case "romanization":
        return <span className={className} key={key}>{romanization.join(' ')} </span>;
      case "falavay":
        return <span className={className} key={key}>{falavay.join('')} </span>;
      case "narrow_transcription":
        return <span className={className} key={key}>{'[' + narrow_transcription.join(' ') + ']'} </span>;
      case "broad_transcription":
        return <span className={className} key={key}>{'/' + broad_transcription.join(' ') + '/'} </span>;
    }
  }
}

function AugmentPair({outline}: {outline: string}) {
  const sharedProps: Omit<InlineGlossProps, "outline"> = {
    language: "lv",
    rows: ["falavay", "romanization"],
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

    getGlossJson({language, outline}).then(gr => {
      if (gr.success) {
        this.setState({content: gr.response});
      } else {
        this.setState({errorMessage: gr.message});
      }
    });
  }

  length = () => this.state.content?.analysis.length || 0;

  render() {
    return (
      <div className={"gloss"}>
        <table>
          <tbody>
            {this.props.rows.map((row, i) => this.renderRow(row, i))}
            {this.props.translation.length > 0 && (
              <tr>
                <td colSpan={this.length() || 1}>
                  {'"' + this.props.translation + '"'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
        {this.state.errorMessage && (
          <p style={{color: "red"}}>
            {this.state.errorMessage}
          </p>
        )}
      </div>
    );
  }

  renderRow(row: GlossRow, key: number) {
    if (this.state.content === undefined) {
      return null;
    }

    return (
      <tr key={key}>
        {this.state.content[row].map((word, col) =>
          <td className={ROW_CLASSES[row]} key={col}>
            {row === "broad_transcription" && col === 0 && '/'}
            {row === "narrow_transcription" && col === 0 && '[ '}
            {word}
            {row === "broad_transcription" && col === this.length() - 1 && '/'}
            {row === "narrow_transcription" && col === this.length() - 1 && ' ]'}
          </td>
        )}
      </tr>
    );
  }
}

function renderMarkdownPreformatted(pre: MarkdownPreformatted) {
  const {language, rows} = parseGlossSpec(pre.language);

  const lines = pre.children[0].content.split("\n").filter(s => s !== "");

  return <BlockGloss outline={lines[0]} translation={lines[1]} {...{language, rows}}/>;
}

export {
  BlockGloss,
  InlineGloss,
  AugmentPair,
  renderInlineCode,
  renderMarkdownPreformatted,
};