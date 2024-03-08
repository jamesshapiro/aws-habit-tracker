import React from 'react';

function SurveyItem({ children, value, onChange }) {
  const handleRatingChange = (event) => {
    onChange(event.target.value);
  };
  return (
    <div>
      {children.DISPLAY_NAME.S}
        <fieldset>
          <legend>
            Select rating:
          </legend>
          
          {VALID_RATINGS.map(option => (
            <div key={option}>
              <input
                type="radio"
                name="current-rating"
                id={option}
                value={option}
                // checked={value === option}
                required
                onChange={handleRatingChange}
              />
              <label htmlFor={option}>
                {option}
              </label>
            </div>
          ))}
        </fieldset>
    </div>
  )
}

const VALID_RATINGS = ["1","2","3","4","5"];

export default SurveyItem;


// function App() {

//   return (
//     <>
//       <form
//         onSubmit={(event) => {
//           event.preventDefault();
//         }}
//       >
//         <fieldset>
//           <legend>
//             Select language:
//           </legend>
          
//           {VALID_LANGUAGES.map(option => (
//             <div key={option}>
//               <input
//                 type="radio"
//                 name="current-language"
//                 id={option}
//                 value={option}
//                 checked={option === language}
//                 onChange={event => {
//                   setLanguage(event.target.value);
//                 }}
//               />
//               <label htmlFor={option}>
//                 {option}
//               </label>
//             </div>
//           ))}
//         </fieldset>
//       </form>
      
//       <p>
//         <strong>Selected language:</strong>
//         {language || "undefined"}
//       </p>
//     </>
//   );
// }

// const VALID_LANGUAGES = [
//   'mandarin',
//   'spanish',
//   'english',
//   'hindi',
//   'arabic',
//   'portugese',
// ];

// export default App;