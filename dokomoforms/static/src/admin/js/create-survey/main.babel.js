'use strict';

import React from 'react';
import ReactDOM from 'react-dom';
import Application from './Application.babel.js';
import { Provider } from 'react-redux';
import { createStore, combineReducers } from 'redux';
import { createReducer } from 'redux-orm';
import bootstrap from './redux/bootstrap.babel.js';
import { orm } from './redux/models.babel.js';
import currentSurveyIdReducer from './redux/reducers.babel.js';

 const rootReducer = combineReducers({
    orm: createReducer(orm),
    currentSurveyId: currentSurveyIdReducer
 });

const store = createStore(rootReducer, bootstrap(orm));

ReactDOM.render(
  <Provider store={store}>
    <Application />
  </Provider>, document.getElementById('app'));