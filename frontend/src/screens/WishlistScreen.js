
import React, { useState, useEffect } from 'react';
import { Container, Box, Typography, Button, CircularProgress, IconButton } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ItemCard from '../components/ItemCard';
import api from '../api';

const WishlistScreen = ({ wishlistId, onBack, onAddItem, onItemClick }) => {
  const [wishlist, setWishlist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWishlist = async () => {
      try {
        const response = await api.get(`/wishlists/${wishlistId}`);
        setWishlist(response.data);
      } catch (err) {
        setError('Failed to fetch wishlist.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchWishlist();
  }, [wishlistId]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Container sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <IconButton onClick={onBack} sx={{ mr: 1 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1">
          {wishlist.name}
        </Typography>
      </Box>
      {wishlist.items.length === 0 ? (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6">This wishlist is empty.</Typography>
          <Typography color="text.secondary">Add your first item to this wishlist.</Typography>
        </Box>
      ) : (
        wishlist.items.map((item) => (
          <ItemCard key={item.id} item={item} onClick={onItemClick} />
        ))
      )}
      <Box sx={{ position: 'fixed', bottom: 24, right: 24 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={onAddItem}
          sx={{ borderRadius: '50%', width: 56, height: 56, minWidth: 0, p: 0 }}
        >
          <AddIcon />
        </Button>
      </Box>
    </Container>
  );
};

export default WishlistScreen;
