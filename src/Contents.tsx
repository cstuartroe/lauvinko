import React, { Component } from "react";

import { SectionDefinition } from "./types";
import PageManager from "./PageManager";

type SLLProps = {
  subsections: string[],
  section_number: number[],
}

function SectionLinkList({subsections, section_number}: SLLProps) {
  return (
    <ul>
      {subsections.map((name, i) => {
        const section = PageManager.get(name);
        if (section === undefined) {
          return null;
        }

        const subsection_number = section_number.concat([i + 1]);

        const link_text = subsection_number.join('.') + " " + section.title;
        return <div key={i}>
          <a href={"/" + section.name} key={i}>
            <li>{link_text}</li>
          </a>
          {section.subsections &&
            <SectionLinkList
                subsections={section.subsections}
                section_number={subsection_number}
            />
          }
        </div>;
      })}
    </ul>
  );
}

class SectionLinks extends Component<{}> {
  render() {
    return (
      <div className="scroll" style={{maxHeight: "75vh"}}>
        <SectionLinkList
          subsections={PageManager.rootSections}
          section_number={[]}
        />
      </div>
    );
  }
}

export default SectionLinks;