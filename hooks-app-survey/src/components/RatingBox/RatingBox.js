import React from 'react';

const RATINGS = ['1', '2', '3', '4', '5'];

const RatingBox = ({ id, category, onRatingChange, attemptedSubmit = undefined }) => {
  const [selectedRating, setSelectedRating] = React.useState(null);

  const handleSelect = (rating) => {
    setSelectedRating(selectedRating === rating ? rating : rating);
    onRatingChange(id, rating);
  };

  return (
    <div>
      <div>{category}</div>
      <div style={{ display: 'flex' }}>
        {RATINGS.map((rating) => (
          <div
            key={rating}
            onClick={() => handleSelect(rating)}
            style={{
              width: '50px',
              height: '50px',
              backgroundColor: selectedRating === rating ? 'darkgrey' : 'lightgrey',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '5px',
              cursor: 'pointer',
            }}
          >
            {rating}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RatingBox;