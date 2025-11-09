
import React, { useState, useEffect } from 'react';
import { Container, Box, Typography, Button, CircularProgress, IconButton, CardMedia } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import DeleteIcon from '@mui/icons-material/Delete';
import api from '../api';
import { useTelegram } from '../hooks/useTelegram';

const ItemScreen = ({ itemId, wishlistId, onBack }) => {
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const tg = useTelegram();

  useEffect(() => {
    const fetchItem = async () => {
      try {
        const response = await api.get(`/wishlists/${wishlistId}`);
        const currentItem = response.data.items.find(i => i.id === itemId);
        if (currentItem) {
          setItem(currentItem);
        } else {
          setError('Item not found.');
        }
      } catch (err) {
        setError('Failed to fetch item.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchItem();
  }, [itemId, wishlistId]);

  const handleDelete = () => {
    tg.showConfirm('Are you sure you want to delete this item?', async (confirmed) => {
      if (confirmed) {
        try {
          await api.delete(`/items/${itemId}`);
          onBack();
        } catch (err) {
          console.error('Failed to delete item', err);
        }
      }
    });
  };

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

  if (!item) {
    return null;
  }

  return (
    <Container sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <IconButton onClick={onBack} sx={{ mr: 1 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1" noWrap>
          {item.title}
        </Typography>
      </Box>
      {item.image_url && (
        <CardMedia
          component="img"
          image={item.image_url}
          alt={item.title}
          sx={{ mb: 2, borderRadius: '8px', maxHeight: 400 }}
        />
      )}
      <Typography variant="h5" component="h2" gutterBottom>
        {item.title}
      </Typography>
      {item.description && (
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          {item.description}
        </Typography>
      )}
      {item.url && (
        <Button
          variant="contained"
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          sx={{ mb: 2 }}
        >
          View Product
        </Button>
      )}
      <Button
        variant="outlined"
        color="error"
        startIcon={<DeleteIcon />}
        onClick={handleDelete}
      >
        Delete Item
      </Button>
    </Container>
  );
};

export default ItemScreen;
