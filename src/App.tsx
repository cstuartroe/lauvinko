import React, { Component } from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";

import "../static/scss/main.scss";

class App extends Component {
  render() {
    return (
        <Router>
          <Switch>
            <Route exact={true} path="" render={() => (
              <p>Hello, World!</p>
            )}/>
          </Switch>
        </Router>
    );
  }
}

export default App;
