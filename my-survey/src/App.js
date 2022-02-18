//aws cloudfront create-invalidation --distribution-id E2I2LGCAG9S89X --paths "/*"
//aws s3 cp --recursive build/ s3://cdkhabits-habitssurveyweakerpotionscombucket15fc8-19lebhcy753i2
import './App.css'
import React from 'react'
import * as Survey from 'survey-react'

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

  getHabitId = (title) =>
    title.charAt(0).toLowerCase() + title.replaceAll(' ', '-').slice(1)

  getHabits = () => {
    console.log('Getting Habits')
    const params = new Proxy(new URLSearchParams(window.location.search), {
      get: (searchParams, prop) => searchParams.get(prop),
    })
    console.log(params)
    const mega_ulid = params.mega_ulid
    const url = process.env.REACT_APP_SURVEY_URL + `?mega_ulid=${mega_ulid}`
    fetch(url, {
      method: 'GET',
    })
      .then((response) => response.json())
      .then((data) => {
        const habitItems = data.Items.map((item) => {
          return item.SK1.S.slice(6)
        })
        const nonGitHubItems = habitItems.filter(item => !item.toLowerCase().includes('github'))
        var newState = { habits: [...nonGitHubItems], isMounted: true }
        this.setState(newState)
      })
  }

  getSurveyJson = () => {
    return {
      pages: [
        {
          name: 'page1',
          elements: this.getSurvey(),
        },
      ],
    }
  }

  getSurvey = () => {
    return this.state.habits.map((habit) => {
      return {
        type: 'rating',
        name: this.getTitle(habit),
        isRequired: true,
        randomprop: 'randomprop',
        minRateDescription: 'Awful',
        maxRateDescription: 'Great'
      }
    })
  }

  componentDidMount() {
    console.log('mounting...')
    this.getHabits()
  }

  sendDataToServer = (survey) => {
    const params = new Proxy(new URLSearchParams(window.location.search), {
      get: (searchParams, prop) => searchParams.get(prop),
    })
    const my_ulid = params.mega_ulid
    const user = params.user
    const data = {}
    const surveyData = survey.data
    data.data_points = {}
    Object.keys(surveyData).forEach((surveyKey) => {
      const habitId = this.getHabitId(surveyKey)
      data.data_points[habitId] = surveyData[surveyKey]
    })
    const url = process.env.REACT_APP_SURVEY_URL
    data.token = my_ulid
    data.user = user
    fetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  render() {
    Survey.StylesManager.applyTheme('modern')
    Survey.StylesManager.ThemeColors['default']['$body-background-color'] =
      'red'

    const params = new Proxy(new URLSearchParams(window.location.search), {
      get: (searchParams, prop) => searchParams.get(prop),
    })
    let date_string = params.date_string
    // let s_time = ulid.decodeTime(my_ulid)
    // let date = new Date(s_time)
    const dd = date_string.slice(-2)
    const mm = date_string.slice(5,7)
    const yyyy = date_string.slice(0, 4)
    return (
      <div className="App">
        <h1 className="habit-title">
          {' '}
          Rate {mm}-{dd}-{yyyy} from 1 (awful) to 5 (great){' '}
        </h1>
        {this.state.isMounted && (
          <div className="enclose">
            <Survey.Survey
              json={this.getSurveyJson()}
              onComplete={this.sendDataToServer}
            />
          </div>
        )}
      </div>
    )
  }
}

export default App
