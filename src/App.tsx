import React, { Component } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import Home from "./Home";
import Page from "./Page";
import Builder from "./Builder";
import Dictionary from "./Dictionary";

import "../static/scss/main.scss";

type State = {
    contents: {
        subsections: [],
    }
}

const router = createBrowserRouter([
    {
        path: "/",
        element: <Home/>,
    },
    {
        path: "/build",
        element: <Builder/>
    },
    {
        path: "/kasanic_dictionary",
        element: <Dictionary
          origin_languages={["kasanic"]}
          page_name="kasanic_dictionary"
        />,
    },
    {
        path: "/loanword_dictionary",
        element: <Dictionary
          origin_languages={["sanskrit", "malay", "javanese", "hokkien", "khmer", "dutch"]}
          page_name="loanword_dictionary"
        />,
    },
    {
        path: "/:name",
        element: <Page/>,
    },
]);

class App extends Component<{}, State> {
    constructor(props: {}) {
        super(props);

        this.state = {
            contents: {
                subsections: []
            },
        };
    }

    render() {
        const constructionNotice = (
          <p style={{textAlign: "center", color: "#dd9900"}}>
              This site is still under construction. You may see some technical glitches, and many pages
              have yet to be copied over from their existing PDF form. You may find a PDF grammar of Lauvìnko{' '}
              <a href="https://drive.google.com/file/d/1ANPILQxHbW6BL1MbSJAIkR2sGIjO-8s3/view?usp=sharing">here</a>.
          </p>
        );

        return (
            <div id="mainframe" className="container-fluid">
                <div className="row">
                    <div className="col-0 col-sm-1 col-md-2 col-lg-3"/>
                    <div className="col-12 col-sm-10 col-md-8 col-lg-6">
                        {constructionNotice}
                        <RouterProvider router={router} />
                    </div>
                    <div className="col-1 col-md-2"/>
                </div>
            </div>
        );
    }
}

export default App;
