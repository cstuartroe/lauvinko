import React, { Component } from "react";
import {ApiResponse, InlineCode, MarkdownPreformatted} from "./types";

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
      rows: Array.from(row_abbrevs).map(a => {
        const row = ROW_ABBREVS[a];
        if (row === undefined) {
          console.log(`Warning: unknown row key: ${a}`);
        }
        return row;
      }).filter(row => (row !== undefined)),
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
    .then(response => response.json())
    .catch(_e => ({success: false, message: "Unknown error"}));
}

export type GlossData = {
  analysis: string[],
  romanization: string[],
  falavay: string[],
  narrow_transcription: string[],
  broad_transcription: string[],
}

export type GlossResponse = ApiResponse<GlossData>;

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
        return <span className={className} key={key}>{extraFormatting(analysis.join(' '))}</span>;
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

type CopyLinkProps = {
  link: string,
}

type CopyLinkState = {
  copiedPosition: number;
}

const maxCopiedPosition = 30;

class CopyLink extends Component<CopyLinkProps, CopyLinkState> {
  constructor(props: CopyLinkProps) {
    super(props);

    this.state = {
      copiedPosition: maxCopiedPosition,
    }
  }

  render() {
    const opacity = 100 - Math.round(this.state.copiedPosition * 100 / maxCopiedPosition);

    return (
      <span style={{position: "relative"}}>
        <a onClick={() => this.onClick()}>Copy link</a>
        <span style={{
          color: `rgba(127, 127, 127, ${opacity}%)`,
          position: "absolute",
          bottom: this.state.copiedPosition,
          left: 0,
        }}>
          Copied!
        </span>
      </span>
    );
  }

  onClick() {
    navigator.clipboard.writeText(this.props.link).then(_ => {
      this.setState({copiedPosition: 0});
      this.moveCopied();
    });
  }

  moveCopied() {
    if (this.state.copiedPosition < maxCopiedPosition) {
      this.setState({copiedPosition: this.state.copiedPosition + 1});
      setTimeout(() => this.moveCopied(), 10);
    }
  }
}

export function extraFormatting(s: string): JSX.Element[] {
  let out: any[] = [];
  let current: string = "";

  const flush = () => {
    out.push(current);
    current = "";
  }

  let i = 0;
  while (i < s.length) {
    const c = s[i];

    if (c == '$') {
      flush();

      const words = s.substring(i).match(/^\$([a-z0-9:]+)\$/)
      if (words === null) {
        throw "Mismatched dollar signs: " + s;
      }

      out.push(<span className="abbrev" key={i}>{words[1]}</span>);

      i += words[0].length;

    } else if (c == '^') {
      flush();

      if (s[i+1] == '{') {
        const words = s.substring(i).match(/^\^{([^}]+)}/)
        if (words === null) {
          throw "Mismatched braces";
        }

        out.push(<sup key={i}>{words[1]}</sup>);

        i += words[0].length;
      } else {
        out.push(<sup>{s[i+1]}</sup>);
        i += 2;
      }

    } else if (c == '⟨') {
      flush();

      const words = s.substring(i).match(/^⟨([^⟩]+)⟩/)
      if (words === null) {
        throw "Mismatched braces";
      }

      out.push(
        '⟨',
        <span style={{fontStyle: "italic", paddingRight: "2px"}}>{words[1]}</span>,
        '⟩',
      );

      i += words[0].length
    } else if (c == '@') {
      current += '۞';
      i++;
    } else {
      current += c;
      i++;
    }
  }

  out.push(current);

  return out;
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

  render() {
    return <LoadedBlockGloss {...this.props} {...this.state}/>;
  }
}

export type LoadedBlockGlossProps = BlockGlossProps & GlossState

export class LoadedBlockGloss extends Component<LoadedBlockGlossProps, {}> {
  constructor(props: LoadedBlockGlossProps) {
    super(props);
  }
  length = () => this.props.content?.analysis.length || 0;

  render() {
    return (
      <div>
        <div className={"gloss"}>
          <div>
            {this.props.errorMessage && (
              <p style={{color: "red", left: "4px"}}>
                {this.props.errorMessage}
              </p>
            )}
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
          </div>
          <p style={{textAlign: "right"}} className="footer" >
            {this.renderFooter()}
          </p>
        </div>
      </div>
    );
  }

  renderRow(row: GlossRow, key: number) {
    if (this.props.content === undefined) {
      return null;
    }

    return (
      <tr key={key}>
        {this.props.content[row].map((word, col) =>
          <td className={ROW_CLASSES[row]} key={col}>
            {row === "broad_transcription" && col === 0 && '/'}
            {row === "narrow_transcription" && col === 0 && '[ '}
            {row == "analysis" ? extraFormatting(word) : word}
            {row === "broad_transcription" && col === this.length() - 1 && '/'}
            {row === "narrow_transcription" && col === this.length() - 1 && ' ]'}
          </td>
        )}
      </tr>
    );
  }

  renderFooter() {
    const { outline, language, translation } = this.props;

    const path = "/build?" + new URLSearchParams({
      outline,
      language,
      translation
    });

    const link = (new URL(path, window.location.toString())).toString();

    if (window.location.pathname === "/build") {
      return <CopyLink link={link}/>
    } else {
      return <a target="_blank" href={link}>Open in builder</a>;
    }
  }
}

export function getPreParts(pre: MarkdownPreformatted) {
  const lines = pre.children[0].content.split("\n");
  let outline = "", i = 0;

  while (lines[i] != "") {
    outline += lines[i] + " ";
    i++;
  }

  const translation = lines.slice(i + 1).join(' ');

  return {outline, translation};
}

function renderMarkdownPreformatted(pre: MarkdownPreformatted) {
  const {language, rows} = parseGlossSpec(pre.language);
  const {outline, translation} = getPreParts(pre)

  return <BlockGloss {...{language, rows, outline, translation}}/>;
}

export {
  BlockGloss,
  InlineGloss,
  AugmentPair,
  renderInlineCode,
  renderMarkdownPreformatted,
};