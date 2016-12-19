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


/*
 * action creators
 */

export function addNode(message) {
  return {
  	type: 'ADD_NODE',
  	node: node
  };
}

export function updateNode(index) {
  return {
  	type: 'TOGGLE_TODO',
  	index: index
  };
}

