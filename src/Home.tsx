import React, { Component } from "react";

import SectionLinks from "./SectionLinks";
import Contents from "./Contents";
import PageManager from "./PageManager";

class Home extends Component {
  render() {
    return (
      <div>
        <h1 style={{marginTop: "3vh"}}>Lauvìnko</h1>

        <img
          src="/static/img/LotusWithText.png"
          style={{width: "30vh", height: "30vh", margin: "2em auto"}}
          alt={"lotus"}
        />

        <p style={{textAlign: "center", padding: ".5em"}}>
          Lauvìnko is a constructed language created by Conor Stuart Roe.
          The table of contents for this site can be found at the bottom.
        </p>

        <p style={{textAlign: "center", padding: ".5em"}}>
          Not sure what to read first? Here are a few
          good places to start to get a feel for the project!
        </p>

        <SectionLinks sections={[
          "introduction",
          "lesson1",
          "north_wind",
        ]}/>

        <p style={{textAlign: "center", padding: ".5em"}}>
          These are some of my favorite pages:
        </p>

        <SectionLinks sections={[
          "colors",
          "proto",
          "case_aspect_interaction",
        ]}/>

        <p style={{textAlign: "center", padding: ".5em"}}>
          For those interested in the whole shebang, here are all {PageManager.orderedPages.length} pages on this site:
        </p>

        <Contents/>
      </div>
    );
  }
}

export default Home;