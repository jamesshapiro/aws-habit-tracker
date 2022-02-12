//aws cloudfront create-invalidation --distribution-id E2I2LGCAG9S89X --paths "/*"
import logo from './logo.svg';
import './App.css'
import React from 'react'
import * as Survey from 'survey-react'
import * as ulid from 'ulid'

class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      habits: [],
      isMounted: false,
    }
  }
  getTitle = (habitName) =>
    habitName.charAt(0).toUpperCase() + habitName.replaceAll('-', ' ').slice(1)

  getHabits = () => {
    var url = process.env.REACT_APP_GET_HABITS_URL
    fetch(url, {
      method: 'GET',
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data)
        const habitItems = data.Items.map((item) => {
          return item.SK1.S.slice(6)
        })
        var newState = { habits: [...habitItems], isMounted: true }
        this.setState(newState)
      })
  }

  getSurveyJson = () => {
    return {
      pages: [
        {
          name: 'page1',
          elements: this.getSurvey()
        },
      ],
    }
  }

  getSurvey = () => {
    return this.state.habits.map((habit) => {
      return { type: 'rating', name: this.getTitle(habit), isRequired: true }
    })
  }

  componentDidMount() {
    this.getHabits()
  }

  
  sendDataToServer(survey) {
    alert("The results are:" + JSON.stringify(survey.data));
  }

  render() {
    Survey.StylesManager.applyTheme('defaultV2')

    const params = new Proxy(new URLSearchParams(window.location.search), {
      get: (searchParams, prop) => searchParams.get(prop),
    });
    let my_ulid = params.ulid
    let s_time = ulid.decodeTime(my_ulid)
    console.log(s_time)
    let date = new Date(s_time)
    console.log(date)
    const dd = String(date.getDate())
    const mm = String(date.getMonth() + 1)
    const yyyy = date.getFullYear()
    return (
      <div className="App">
        <h1 className="habit-title">
          {' '}
          Rate {mm}-{dd}-{yyyy} from 1 (awful) to 5 (great){' '}
        </h1>
        {this.state.isMounted && (
          <Survey.Survey
            json={this.getSurveyJson()}
            onComplete={this.sendDataToServer}
          />
        )}
      </div>
    )
  }
}

export default App
