
import React, { useState, useEffect } from 'react';
import { Container, Box, Typography, Button, CircularProgress } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import WishlistCard from '../components/WishlistCard';
import api from '../api';

const MainScreen = ({ onWishlistClick, onCreateWishlist }) => {
  const [wishlists, setWishlists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWishlists = async () => {
      try {
        const response = await api.get('/wishlists');
        setWishlists(response.data);
      } catch (err) {
        setError('Failed to fetch wishlists.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchWishlists();
  }, []);

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
      <Typography variant="h4" component="h1" gutterBottom>
        My Wishlists
      </Typography>
      {wishlists.length === 0 ? (
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6">No wishlists yet.</Typography>
          <Typography color="text.secondary">Create your first wishlist to get started.</Typography>
        </Box>
      ) : (
        wishlists.map((wishlist) => (
          <WishlistCard key={wishlist.id} wishlist={wishlist} onClick={onWishlistClick} />
        ))
      )}
      <Box sx={{ position: 'fixed', bottom: 24, right: 24 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={onCreateWishlist}
          sx={{ borderRadius: '50%', width: 56, height: 56, minWidth: 0, p: 0 }}
        >
          <AddIcon />
        </Button>
      </Box>
    </Container>
  );
};

export default MainScreen;
