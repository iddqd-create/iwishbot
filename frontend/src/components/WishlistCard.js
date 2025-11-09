
import React from 'react';
import { Paper, Typography, Box } from '@mui/material';

const WishlistCard = ({ wishlist, onClick }) => {
  return (
    <Paper
      elevation={3}
      onClick={() => onClick(wishlist.id)}
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
      <Typography variant="h6" component="h3" gutterBottom>
        {wishlist.name}
      </Typography>
      <Box sx={{ color: 'text.secondary' }}>
        <Typography variant="body2">
          {wishlist.item_count} {wishlist.item_count === 1 ? 'item' : 'items'}
        </Typography>
      </Box>
    </Paper>
  );
};

export default WishlistCard;
