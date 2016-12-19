'use strict';

import React from 'react';
import ReactDOM from 'react-dom';
import Application from './Application.babel.js';
import { Provider } from 'react-redux';
import { createStore } from 'redux';
import reducers from './redux/reducers.babel.js';

let store = createStore(reducers);

ReactDOM.render(
  <Provider store={store}>
    <Application />
  </Provider>, document.getElementById('app'));