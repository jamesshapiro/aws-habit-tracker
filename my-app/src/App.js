//aws cloudfront create-invalidation --distribution-id E70XD704NPJDM --paths "/*"
//aws s3 cp --recursive build/ s3://cdkhabits-habitsweakerpotionscombucketdff06391-116yh481gtpp6
import logo from './logo.svg';
import './App.css';
import React from 'react'
import Habit from './components/Habit/Habit'

class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      habits: [],
      isMounted: false
    }
  }
  getNewEntries = () => {
    var james = "james" 
    var url =
      process.env.REACT_APP_GET_HABITS_URL + `?user=${james}`
    fetch(url, {
      method: 'GET',
    })
      .then((response) => response.json())
      .then((data) => {
        const habitItems = data.Items.map((item) => {
          return {
            habitName: item.SK1.S.slice(6),
            habitColor: item.COLOR.S
          }
        })
        var newState = { habits: [...habitItems], isMounted: true }
        this.setState(newState)
      })
  }

  getHabitGraphs = () => {
    return <div className="habit-graphs">
      {this.state.habits.map(habit => {
        return <Habit habitName={habit.habitName} habitColor={habit.habitColor} />
      })}
    </div>
  }

  componentDidMount() {
    this.getNewEntries()
  }

  render() {
    return (
      <div className="App">
        <h1 className="habit-title">Habit Tracker</h1>
        {this.state.isMounted && this.getHabitGraphs()}
      </div>
    )
  }
}

export default App;
