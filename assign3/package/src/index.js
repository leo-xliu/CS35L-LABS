import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

  
  function Square(props){
      return(
        <button className="square" onClick={props.onClick}>
            {props.value}
        </button>
      );
  }

  class Board extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            squares: Array(9).fill(null),
            xIsNext: true,
            count: Array(2).fill(0),
            firstClick: true,
            firstClickIndex: null,
            invalidMove: false,
            hasCenter: null,
        };
    }
    handleClick(i) {
        const squares = this.state.squares.slice();
        if (calculateWinner(squares)){ //dont update if game won
            return;
        }
        let j = 0; //indicator of whose turn it is
        const count = this.state.count.slice();
        if (!this.state.xIsNext){
          j=1;
        }
        if (this.state.count[j] < 3){ //when we have not reached 3 pieces
          if (squares[i]){ //dont update if there is already a symbol
            return;
          }
          squares[i] = this.state.xIsNext ? 'X' : 'O'; 
          count[j] = count[j] + 1;
          this.setState({squares: squares, xIsNext: !this.state.xIsNext, count: count, hasCenter: squares[4] });
        }
        else {    //when 3 pieces exist
          let curSym = ['X', 'O'];
          if (this.state.firstClick){
            if (squares[i] == null || squares[i] !== curSym[j]){ //must be same piece type
              return;
            }
            else{
              this.setState({firstClick: false, firstClickIndex: i, invalidMove: false}); //store first click as which piece to move in second click
            }
          }
          else { //second click
            if (squares[i] != null){ //needs to be open space
              this.setState({firstClick: true, invalidMove: true});
            }
            else if (isValidMove(this.state.firstClickIndex, i)){  //check move validity
              squares[this.state.firstClickIndex] = null;
              squares[i] = this.state.xIsNext ? 'X' : 'O';
              if (this.state.hasCenter === curSym[j] && !calculateWinner(squares) && this.state.firstClickIndex !== 4){
                this.setState({firstClick: true, invalidMove: true});
              }
              else{
                this.setState({squares: squares, xIsNext: !this.state.xIsNext, firstClick: true, invalidMove: false, hasCenter: squares[4]});
              }
            }
            else{
              this.setState({firstClick: true, invalidMove: true});
            }
          }
        }
    }
    renderSquare(i) {
      return (
        <Square 
            value={this.state.squares[i]}
            onClick={() => this.handleClick(i)}
            />
        );
    }
  
    render() {
      const winner = calculateWinner(this.state.squares);
      let status;
      let moveStatus = null;
      if (winner){
          status =  'Winner: ' + winner;
      }
      else{
          status = 'Next player: ' + (this.state.xIsNext ? 'X' : 'O');
          if (this.state.firstClick && this.state.count[0] === 3 && this.state.count[1] === 3 && !this.state.invalidMove){
            moveStatus = 'Choose one of your pieces!';
          }
          else if (!this.state.firstClick && !this.state.invalidMove){
            moveStatus = 'Make a move!';
          }
          else if (this.state.invalidMove){
            moveStatus = 'Invalid Move! Choose one of your pieces again!';
          }
      }
      return (
        <div>
          <div className="status">{status}</div>
          <div className="board-row">
            {this.renderSquare(0)}
            {this.renderSquare(1)}
            {this.renderSquare(2)}
          </div>
          <div className="board-row">
            {this.renderSquare(3)}
            {this.renderSquare(4)}
            {this.renderSquare(5)}
          </div>
          <div className="board-row">
            {this.renderSquare(6)}
            {this.renderSquare(7)}
            {this.renderSquare(8)}
          </div>
          <div className="moveStatus">{moveStatus}</div>
        </div>
      );
    }
  }
  
  class Game extends React.Component {
    render() {
      return (
        <div className="game">
          <div className="game-board">
            <Board />
          </div>
          <div className="game-info">
            <div>{/* status */}</div>
            <ol>{/* TODO */}</ol>
          </div>
        </div>
      );
    }
  }
  
  // ========================================
  
  const root = ReactDOM.createRoot(document.getElementById("root"));
  root.render(<Game />);
  
  function calculateWinner(squares) {
      const lines = [
          [0,1,2],
          [3,4,5],
          [6,7,8],
          [0,3,6],
          [1,4,7],
          [2,5,8],
          [0,4,8],
          [2,4,6],
      ];
      for (let i = 0; i < lines.length; i++){
          const [a, b, c] = lines[i];
          if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]){
              return squares[a];
          }
      }
      return null;
  }

  function isValidMove(fcIndex, scIndex){
    switch(fcIndex){
      case 0: 
        if (scIndex === 1 || scIndex === 3 || scIndex === 4){
          return true;
        }
        break;
      case 1:
        if (scIndex === 0 || scIndex === 2 || scIndex === 3 || scIndex === 4 || scIndex === 5){
          return true;
        }
        break;
      case 2:
        if (scIndex === 1 || scIndex === 4 || scIndex === 5){
          return true;
        }
        break;
      case 3:
        if (scIndex === 0 || scIndex === 1 || scIndex === 4 || scIndex === 6 || scIndex === 7){
          return true;
        }
        break;
      case 4:
        return true;
      case 5:
        if (scIndex === 1 || scIndex === 2 || scIndex === 4 || scIndex === 7 || scIndex === 8){
          return true;
        }
        break;
      case 6:
        if (scIndex === 3 || scIndex === 4 || scIndex === 7){
          return true;
        }
        break;
      case 7: 
        if (scIndex === 3 || scIndex === 4 || scIndex === 5 || scIndex === 6 || scIndex === 8){
          return true;
        }
        break;
      case 8:
        if (scIndex === 4 || scIndex === 5 || scIndex === 7){
          return true;
        }
        break;
      default:
        break;
    }
    return false;
  }