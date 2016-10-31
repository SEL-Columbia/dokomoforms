class NodeList extends React.Component {

    constructor(props) {
        super(props);

        this.addToNodeList = this.addToNodeList.bind(this);
        this.addQuestion = this.addQuestion.bind(this);
        this.listQuestions = this.listQuestions.bind(this);
        
        this.state = {
            questions: 1,
            nodes: []
        };
    }

    addToNodeList(newNode) {
        const nodeArr = this.state.nodes;
        nodeArr.push(newNode);
        this.setState({nodes: nodeArr}, function(){
            console.log('added to list!', newNode, this.state.nodes)
            this.props.updateNodes(this.state.nodes);
        })
    }

    addQuestion() {
        let currentQuestions = this.state.questions;
        currentQuestions++;
        this.setState({questions: currentQuestions});
    }

    listQuestions(num) {
        var rows = [];
        for (var i=0; i<num; i++) {
            rows.push(<Node key={i} index={i} addToNodeList={this.addToNodeList} />)
        }
        return rows;
    }

    render() {
        return (
            <div>
                {this.listQuestions(this.state.questions)}
                <button onClick={this.addQuestion}>Add Question</button>
            </div>
        );
    }
}

class Node extends React.Component {

    constructor(props) {
        super(props);

        this.updateTitle = this.updateTitle.bind(this);
        this.saveNode = this.saveNode.bind(this);
        this.state = {
            title: ''
        }
    }

    updateTitle(event) {
        this.setState({title: event.target.value});
    }

    saveNode() {
        console.log('saving from node', this.state);
        const node = this.state;
        this.props.addToNodeList(node);
    }

    render() {
        return (
            <div>
                Question: <input type="text"
                    onChange={this.updateTitle}/>
                    <button onClick={this.saveNode}>save</button>
                    <button onClick={this.addSubsurvey}>add sub-survey</button>
            </div>
        );
    }
}

export default NodeList;