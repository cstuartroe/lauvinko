import React, { Component } from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";

import Home from "./Home";
import Page from "./Page";
// import Dictionary from "./Dictionary";

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
        return (
            <div id="mainframe" className="container-fluid">
                <div className="row">
                    <div className="col-1 col-md-2"/>
                    <div className="col-10 col-md-8">
                        <Router>
                            <Switch>
                                <Route exact={true} path="/" component={Home}/>
                                {/*<Route*/}
                                {/*  exact={true}*/}
                                {/*  path="/kasanic_dictionary"*/}
                                {/*  render={(props) => (*/}
                                {/*    <Dictionary*/}
                                {/*      {...props}*/}
                                {/*      origins={["kasanic"]} page_id="kasanic_dictionary"*/}
                                {/*    />*/}
                                {/*  )}*/}
                                {/*/>*/}
                                {/*<Route*/}
                                {/*  exact={true}*/}
                                {/*  path="/loanword_dictionary"*/}
                                {/*  render={(props) => (*/}
                                {/*    <Dictionary*/}
                                {/*      {...props}*/}
                                {/*      origins={["sanskrit", "malay", "arabic", "tamil", "hokkien", "portuguese", "dutch", "english"]}*/}
                                {/*      page_id="loanword_dictionary"*/}
                                {/*    />*/}
                                {/*  )}*/}
                                {/*/>*/}
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
