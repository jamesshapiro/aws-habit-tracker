//############## PROD ################
//PROD: aws s3 cp --recursive build/ s3://cdkhabits-surveygithabitcombucket4f6ffd5a-1mwnd3a635op9
//PROD: aws cloudfront create-invalidation --distribution-id E8P5WYSXZ0IWD --paths "/*"
// npm run build && aws s3 cp --recursive build/ s3://cdkhabits-surveygithabitcombucket4f6ffd5a-1mwnd3a635op9 && aws cloudfront create-invalidation --distribution-id E8P5WYSXZ0IWD --paths "/*"
//############## DEV ################
//DEV: aws s3 cp --recursive build/ s3://cdkhabits-habitssurveyweakerpotionscombucket15fc8-19lebhcy753i2
//DEV: aws cloudfront create-invalidation --distribution-id E2I2LGCAG9S89X --paths "/*"

import React from 'react';
import useSWR from 'swr';
import RatingBox from '../RatingBox';
import styles from './Survey.module.css';

const params = new Proxy(new URLSearchParams(window.location.search), {
  get: (searchParams, prop) => searchParams.get(prop),
})
const token = params.token
const ENDPOINT = process.env.REACT_APP_SURVEY_URL + `?token=${token}`
let date_string = params.date_string
const dd = date_string.slice(-2)
const mm = date_string.slice(5, 7)
const yyyy = date_string.slice(0, 4)

async function fetcher(endpoint) {
  const response = await fetch(endpoint);
  const json = await response.json();
  return json;
}

function Survey() {
  const { data, isLoading } = useSWR(ENDPOINT, fetcher);
  const [ratings, setRatings] = React.useState({});
  const [attemptedSubmit, setAttemptedSubmit] = React.useState(false);

  const handleRatingChange = (id, newRating) => {
    setRatings(prevRatings => ({
      ...prevRatings,
      [id]: newRating,
    }));
  };

  const handleSubmit = () => {
    const allRated = Object.keys(ratings).length >= data.length;
    if (!allRated) {
      setAttemptedSubmit(true);
      // Handle the error state appropriately (e.g., show a message)
    } else {
      // Proceed with submitting the ratings
    }
  };

  if (data) {
    console.log(data)
    return <div className={styles.surveyContainer}>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          console.log(ratings);
        }}
      >
      <div
        className={styles.header}
      >Rate your tenacity on {mm}-{dd}-{yyyy} (1 = Awful, 5 = Great)</div>
      {data.slice(1).map((habit, index) => 
        <RatingBox 
          key={index}
          id={index}
          category={habit.DISPLAY_NAME.S}
          onRatingChange={handleRatingChange}
          attemptedSubmit={attemptedSubmit} 
        >
            {habit}
        </RatingBox>)}
      <button 
      className={styles.submitButton}
      onClick={handleSubmit}>Submit</button>
      </form>
    </div>;
  }

  return <div>Loading...</div>;
}

export default Survey;



