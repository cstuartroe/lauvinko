import React, { Component } from "react";
import { Link } from "react-router-dom";

import {Language, GlossParams, BlockGloss, GlossRow} from "./Gloss";

type State = GlossParams & {
  renderedOutline: string,
  translation: string,
};

const builderRows: GlossRow[] = [
  "falavay",
  "romanization",
  "broad_transcription",
  "narrow_transcription",
  "analysis",
]

class Builder extends Component<{}, State> {
  constructor(props: {}) {
    super(props);

    this.state = this.generateState();
  }

  generateState(): State {
    const sp = new URLSearchParams(window.location.search);

    return {
      outline: sp.get('outline') || "",
      renderedOutline: sp.get('outline') || "",
      language: (sp.get('language') || "lv") as Language,
      translation: sp.get('translation') || "",
    }
  }

  updateUrl() {
    const {outline, language, translation} = this.state;

    window.location.search = (new URLSearchParams({outline, language, translation})).toString();
  }

  render() {
    return (
      <>
        <h3><Link to={'/'}>Go home</Link></h3>

        <p style={{textAlign: "center"}}>
          Welcome to the Lauvìnko gloss builder!
          <br/>
          Just edit the gloss outline in the text input below and hit "Reload"
          to try rendering the gloss
        </p>

        <div className="row">
          <div className="col-12 col-md-10">
            <input
              type="text"
              value={this.state.outline}
              style={{width: "100%"}}
              onInput={(e) => {
                this.setState({
                  outline: e.currentTarget.value,
                })
              }}
            />
          </div>

          <div className="col-12 col-md-2">
            <button
              style={{margin: 0, padding: 0, height: "100%"}}
              onClick={() => {
                this.updateUrl();
              }}
            >
              Reload
            </button>
          </div>
        </div>

        <div className="row" style={{paddingTop: "10px"}}>
          <div className="col-3 col-md-2">
            <p style={{padding: ".5em"}}>Translation:</p>
          </div>

          <div className="col-9 col-md-10">
            <input
              type="text"
              value={this.state.translation}
              style={{width: "100%"}}
              onInput={(e) => {
                this.setState({
                  translation: e.currentTarget.value,
                })
              }}
            />
          </div>
        </div>

        {this.state.renderedOutline.length > 0 && (
          <BlockGloss
            rows={builderRows}
            outline={this.state.renderedOutline}
            language={this.state.language}
            translation={this.state.translation}
          />
        )}
      </>
    );
  }
}

export default Builder;