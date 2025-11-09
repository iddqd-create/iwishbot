
import React from 'react';
import { Paper, Typography, Box, CardMedia } from '@mui/material';

const ItemCard = ({ item, onClick }) => {
  return (
    <Paper
      elevation={3}
      onClick={() => onClick(item.id)}
      sx={{
        p: 3,
        mb: 2,
        cursor: 'pointer',
        transition: 'transform 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
        },
      }}
    >
      {item.image_url && (
        <CardMedia
          component="img"
          height="140"
          image={item.image_url}
          alt={item.title}
          sx={{ mb: 2, borderRadius: '8px' }}
        />
      )}
      <Typography variant="h6" component="h3" gutterBottom>
        {item.title}
      </Typography>
      {item.description && (
        <Typography variant="body2" color="text.secondary">
          {item.description}
        </Typography>
      )}
    </Paper>
  );
};

export default ItemCard;
