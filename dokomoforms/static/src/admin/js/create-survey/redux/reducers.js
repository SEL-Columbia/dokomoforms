import { combineReducers } from 'redux'
import { ADD_TODO, TOGGLE_TODO, SET_VISIBILITY_FILTER, VisibilityFilters } from './actions'
const { SHOW_ALL } = VisibilityFilters

function visibilityFilter(state = SHOW_ALL, action) {
  switch (action.type) {
    case SET_VISIBILITY_FILTER:
      return action.filter
    default:
      return state
  }
}

function surveys(state, action) {
    switch (action.type) {
        case 'ADD_NODE':
            return Object.assign({}, state, {
                nodes: [
                    ...state.nodes,
                    {
                        id: 123456,
                        node: {}
                    }
                ]
            })
        case 'UPDATE_NODE':

    }
}

function todos(state = [], action) {
  switch (action.type) {
    case 'ADD_TODO':
      var newState = Object.assign({}, state);

      newState.todo.items.push({
        message: action.message,
        completed: false
      })
      // return [
      //   ...state,
      //   {
      //     text: action.text,
      //     completed: false
      //   }
      // ]
    case TOGGLE_TODO:
      return state.map((todo, index) => {
        if (index === action.index) {
          return Object.assign({}, todo, {
            completed: !todo.completed
          })
        }
        return todo
      })
    default:
      return state
  }
}

const todoApp = combineReducers({
  visibilityFilter,
  todos
})

export default todoApp