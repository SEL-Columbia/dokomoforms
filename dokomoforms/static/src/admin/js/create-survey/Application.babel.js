import React from 'react';

class App extends React.Component {
   render() {
      return (
         <div>
            <h1>{this.props.title}</h1>
            <h2>{this.props.type}</h2>
         </div>
      );
   }
}

class Comment extends React.Component {

    constructor(props) {
        super(props);

        this.edit = this.edit.bind(this);
        this.save = this.save.bind(this);

        this.state = {
            editing: false
        };
    }

    edit() {
        this.setState({editing: true});
    }

    remove() {
        alert('Removing comment');
    }

    save() {
        let val = this.refs.newText.value;
        console.log(val);
        this.setState({editing: false});
    }

    renderNormal() {
        console.log(this.props)
        return (
            <div>
                <div>{this.props.children}</div>
                <button onClick={this.edit}>Edit</button>
                <button onClick={this.remove}>Delete</button>
            </div>
        );
    }

    renderForm() {
        return (
            <div>
                <textarea ref="newText" defaultValue={this.props.children}></textarea>
                <button onClick={this.save}>Save</button>
            </div>
        );
    }

    render() {
        if (this.state.editing) {
            return this.renderForm();
        } else {
            return this.renderNormal();
        }
    }
}

class CheckBox extends React.Component {

    constructor(props) {
        super(props);

        this.handleChecked = this.handleChecked.bind(this);

        this.state = {
            checked: true,
            otherstate: 32
        }
    }

    handleChecked() {
        this.setState({checked: !this.state.checked})
    }

    // getInitialState() {
    //     return {checked: true, otherstate: 32}
    // }

    render() {
        var msg;
        if(this.state.checked) {
            msg = 'checked!';
        }else{
            msg = 'unchecked!';
        }
        return (
            <div>
                <input type="checkbox" onChange={this.handleChecked} defaultChecked={this.state.checked}/>
                <h3>Checkbox is {msg}</h3>
            </div>
        );
    }
}

class Board extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            comments: [
                'com1',
                'com2',
                'com3'
            ]
        }
    }

    removeComment() {
        
    }

    eachComment(text, i) {
        return (<Comment key={i} index={i}>{text}</Comment>);
    }

    render() {
        return (
            <div className="board">
                {
                    this.state.comments.map(this.eachComment)
                }
            </div>
        )
    }
}


export { App, Comment, CheckBox, Board };

// constructor(props) {
//         super(props);
//         this.edit = this.edit.bind(this);
//         this.remove = this.remove.bind(this);
//     }


// className in jsx... NOT class