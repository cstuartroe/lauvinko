import React from "react";
import { Link } from "react-router-dom";

import PageManager from "./PageManager";

function linkWidth(numLinks: number) {
  switch (numLinks) {
    case 2:
      return 6;
    case 4:
      return 3;
    default:
      return 4;
  }
}

type Props = {
  sections: string[],
}

export default function SectionLinks({sections}: Props) {
  const width = linkWidth(sections.length);

  return (
    <div className="row">
      {sections.map((section, i) =>
        <div key={i} className={"go-down col-12 col-md-" + width}>
          <Link to={"/" + section} >
            <div>
              <h3>{PageManager.get(section)?.title}</h3>
            </div>
          </Link>
        </div>
      )}
    </div>
  );
}
