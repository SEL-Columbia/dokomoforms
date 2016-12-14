// // adding a new todo item

// const ADD_TODO = 'ADD_TODO'

// {
// 	type: ADD_TODO,
// 	text: 'Build my first Redux app'
// }

// {
// 	type: TOGGLE_TODO,
// 	index: UNIQUE INDEX of data being passed in
// }

// //changing the currently visisble todos
// {
// 	type: SET_VISIBILITY_FILTER,
// 	filter: SHOW_COMPLETED
// }

// // action CREATORS return an action

// function addTodo(text) {
// 	return {
// 		type: ADD_TODO,
// 		text
// 	}
// }

// // to initiate, pass the result to dispatch function

// dispatch(addTodo(text))
// dispatch(completeTodo(index))



/*
 * action types
 */

export const ADD_TODO = 'ADD_TODO'
export const TOGGLE_TODO = 'TOGGLE_TODO'
export const SET_VISIBILITY_FILTER = 'SET_VISIBILITY_FILTER'

/*
 * other constants
 */

export const VisibilityFilters = {
  SHOW_ALL: 'SHOW_ALL',
  SHOW_COMPLETED: 'SHOW_COMPLETED',
  SHOW_ACTIVE: 'SHOW_ACTIVE'
}

/*
 * action creators
 */

export function addTodo(text) {
  return { type: ADD_TODO, text }
}

export function toggleTodo(index) {
  return { type: TOGGLE_TODO, index }
}

export function setVisibilityFilter(filter) {
  return { type: SET_VISIBILITY_FILTER, filter }
}
