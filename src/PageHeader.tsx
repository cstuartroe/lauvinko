import React, { Component } from "react";
import { Link } from "react-router-dom";

import PageManager from "./PageManager";

type Props = {
  name: string,
  show_title: boolean,
}

class PageHeader extends Component<Props> {
  render() {
    const { name, show_title } = this.props;
    const section = PageManager.get(name);
    const pageIndex = PageManager.indexOf(name);

    const prev = PageManager.byIndex(pageIndex - 1);
    const next = pageIndex === -1 ? undefined : PageManager.byIndex(pageIndex + 1);
    const parent = section?.parent ? PageManager.get(section.parent) : undefined;

    return (
      <div>
        {show_title && section && <h1 style={{marginTop: "3vh"}}>{section.title}</h1>}
        <div className="row">
          <div className="col-12 col-md-4">
            {prev ?
              <p className="go-up">
                <Link to={"/" + prev.name}>← {prev.title}</Link>
              </p>
              : null
            }
          </div>

          <div className="col-12 col-md-4">
            {parent ?
              <p className="go-up">
                <Link to={"/" + parent.name}>Go up to {parent.title}</Link>
              </p>
              :
              <p className="go-up">
                <Link to={"/"}>Go up to index page</Link>
              </p>
            }
          </div>

          <div className="col-12 col-md-4">
            {next ?
              <p className="go-up">
                <Link to={"/" + next.name}>{next.title} →</Link>
              </p>
              : null
            }
          </div>
        </div>
      </div>
    );
  }
}

export default PageHeader;