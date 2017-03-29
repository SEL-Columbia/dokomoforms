import React from 'react';
import ReactDOM from 'react-dom';
import configureStore from 'redux-mock-store';
import { Provider } from 'react-redux';
import { combineReducers } from 'redux';
import { createReducer } from 'redux-orm';
import bootstrap from '../../redux/bootstrap.babel.js';
import { orm } from '../../redux/models.babel.js';
import Application from '../../Application.babel.js';
import Survey from '../Survey.babel.js';
import currentSurveyIdReducer from '../../redux/reducers.babel.js';
import renderer from 'react-test-renderer';

const middlewares = []
const mockStore = configureStore(middlewares)

// You would import the action from your codebase in a real scenario

it('renders correctly', () => {

	const initialState = {}
  const store = mockStore(initialState)

  const tree = renderer.create(
    <Provider store={store}>
    	<Application />
  	</Provider>
  ).toJSON();
  expect(tree).toMatchSnapshot();
});