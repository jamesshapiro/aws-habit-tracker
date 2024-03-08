import React from 'react';
import useSWR from 'swr';
import SurveyItem from '../SurveyItem';

const params = new Proxy(new URLSearchParams(window.location.search), {
  get: (searchParams, prop) => searchParams.get(prop),
})
const token = params.token
const ENDPOINT = process.env.REACT_APP_SURVEY_URL + `?token=${token}`

async function fetcher(endpoint) {
  const response = await fetch(endpoint);
  const json = await response.json();
  return json;
}

function Survey() {
  const { data, isLoading } = useSWR(ENDPOINT, fetcher);
  const [ratings, setRatings] = React.useState({});

  const handleRatingChange = (index, newRating) => {
    setRatings(prevRatings => ({
      ...prevRatings,
      [index]: newRating,
    }));
  };

  if (data) {
    return <div>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          console.log(ratings);
        }}
      >
      {data.map((habit, index) => 
        <SurveyItem 
          key={index}
          value={ratings[index] || ''}
          onChange={(newRating) => handleRatingChange(index, newRating)}
        >
            {habit}
        </SurveyItem>)}
      <button type="submit">Submit</button>
      </form>
    </div>;
  }

  return <div>Loading...</div>;
}

export default Survey;



// function App() {
//   const { data, error } = useSWR(ENDPOINT, fetcher);
  
//   console.log(data, error);
  
//   return (
//     <p>
//       Current temperature:
//       {typeof data?.temperature === 'number' && (
//         <span className="temperature">
//           {data.temperature}°C
//         </span>
//       )}
//     </p>
//   );
// }

// export default App;

//############## PROD ################
//PROD: aws s3 cp --recursive build/ s3://cdkhabits-surveygithabitcombucket4f6ffd5a-1mwnd3a635op9
//PROD: aws cloudfront create-invalidation --distribution-id E8P5WYSXZ0IWD --paths "/*"
// npm run build && aws s3 cp --recursive build/ s3://cdkhabits-surveygithabitcombucket4f6ffd5a-1mwnd3a635op9 && aws cloudfront create-invalidation --distribution-id E8P5WYSXZ0IWD --paths "/*"
//############## DEV ################
//DEV: aws s3 cp --recursive build/ s3://cdkhabits-habitssurveyweakerpotionscombucket15fc8-19lebhcy753i2
//DEV: aws cloudfront create-invalidation --distribution-id E2I2LGCAG9S89X --paths "/*"


// class App extends React.Component {
//   constructor(props) {
//     super(props)
//     this.state = {
//       habits: [],
//       isMounted: false,
//     }
//   }

//   getHabitId = (habitName) => habitName.toLowerCase().split(/\s+/).join('-')

//   getHabits = () => {
//     const params = new Proxy(new URLSearchParams(window.location.search), {
//       get: (searchParams, prop) => searchParams.get(prop),
//     })
//     const token = params.token
//     const url = process.env.REACT_APP_SURVEY_URL + `?token=${token}`
//     fetch(url, {
//       method: 'GET',
//     })
//       .then((response) => response.json())
//       .then((data) => {
//         const habitItems = data.map((item) => {
//           return item
//         })
//         const nonGitHubItems = habitItems.filter(
//           (item) => !item.DISPLAY_NAME.S.toLowerCase().includes('github')
//         )
//         var newState = { habits: [...nonGitHubItems], isMounted: true }
//         this.setState(newState)
//       })
//   }

//   getSurveyJson = () => {
//     return {
//       pages: [
//         {
//           name: 'page1',
//           elements: this.getSurvey(),
//         },
//       ],
//     }
//   }

//   getSurvey = () => {
//     return this.state.habits.map((habit) => {
//       console.log(habit)
//       return {
//         type: 'rating',
//         name: habit.DISPLAY_NAME.S,
//         isRequired: true,
//         randomprop: 'randomprop',
//         minRateDescription: 'Awful',
//         maxRateDescription: 'Great',
//       }
//     })
//   }

//   componentDidMount() {
//     this.getHabits()
//   }

//   sendDataToServer = (survey) => {
//     const params = new Proxy(new URLSearchParams(window.location.search), {
//       get: (searchParams, prop) => searchParams.get(prop),
//     })
//     const token = params.token
//     const data = {}
//     const surveyData = survey.data
//     data.data_points = {}
//     Object.keys(surveyData).forEach((surveyKey) => {
//       const habitId = this.getHabitId(surveyKey)
//       data.data_points[habitId] = surveyData[surveyKey]
//     })
//     const url = process.env.REACT_APP_SURVEY_URL
//     data.token = token
//     fetch(url, {
//       method: 'POST',
//       body: JSON.stringify(data),
//     })
//     setTimeout(() => {
//       window.location.href = 'https://githabit.com'
//     }, 1200)
//   }

//   render() {
//     Survey.StylesManager.applyTheme('modern')
//     const params = new Proxy(new URLSearchParams(window.location.search), {
//       get: (searchParams, prop) => searchParams.get(prop),
//     })
//     let date_string = params.date_string
//     const dd = date_string.slice(-2)
//     const mm = date_string.slice(5, 7)
//     const yyyy = date_string.slice(0, 4)
//     return (
//       <div className="App">
//         <h2 className="habit-title">
//           {' '}
//           Rate your tenacity on {mm}-{dd}-{yyyy}
//         </h2>
//         {this.state.isMounted && (
//           <div className="enclose">
//             <Survey.Survey
//               json={this.getSurveyJson()}
//               onComplete={this.sendDataToServer}
//             />
//           </div>
//         )}
//         <div className="survey-footer"></div>
//       </div>
//     )
//   }
// }

// export default App
