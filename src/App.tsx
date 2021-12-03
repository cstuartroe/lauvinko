import React, { Component } from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";

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
                    <div className="col-1 col-md-2"/>
                    <div className="col-10 col-md-8">
                        {constructionNotice}
                        <Router>
                            <Switch>
                                <Route exact={true} path="/" component={Home}/>
                                <Route exact={true} path="/build" component={Builder}/>
                                <Route
                                  exact={true}
                                  path="/kasanic_dictionary"
                                  render={(props) => (
                                    <Dictionary
                                      {...props}
                                      origin_languages={["kasanic"]}
                                      page_name="kasanic_dictionary"
                                    />
                                  )}
                                />
                                <Route
                                  exact={true}
                                  path="/loanword_dictionary"
                                  render={(props) => (
                                    <Dictionary
                                      {...props}
                                      origin_languages={["sanskrit"]}
                                      page_name="loanword_dictionary"
                                    />
                                  )}
                                />
                                <Route path="/:name" render={({match}) => (
                                  <Page name={match.params.name}/>
                                )}/>
                            </Switch>
                        </Router>
                    </div>
                    <div className="col-1 col-md-2"/>
                </div>
            </div>
        );
    }
}

export default App;
