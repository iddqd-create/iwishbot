import React, { useState } from 'react';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import theme from './theme/theme';
import { useTelegram } from './hooks/useTelegram';
import MainScreen from './screens/MainScreen';
import WishlistScreen from './screens/WishlistScreen';
import CreateWishlistScreen from './screens/CreateWishlistScreen';
import AddItemScreen from './screens/AddItemScreen';
import ItemScreen from './screens/ItemScreen';

function App() {
  useTelegram();
  const [currentScreen, setCurrentScreen] = useState('main');
  const [selectedWishlistId, setSelectedWishlistId] = useState(null);
  const [selectedItemId, setSelectedItemId] = useState(null);

  const handleWishlistClick = (wishlistId) => {
    setSelectedWishlistId(wishlistId);
    setCurrentScreen('wishlist');
  };

  const handleCreateWishlist = () => {
    setCurrentScreen('create-wishlist');
  };

  const handleWishlistCreated = (wishlistId) => {
    setSelectedWishlistId(wishlistId);
    setCurrentScreen('wishlist');
  };

  const handleBack = () => {
    if (currentScreen === 'add-item' || currentScreen === 'item') {
      setCurrentScreen('wishlist');
      setSelectedItemId(null);
    } else {
      setCurrentScreen('main');
      setSelectedWishlistId(null);
      setSelectedItemId(null);
    }
  };

  const handleAddItem = () => {
    setCurrentScreen('add-item');
  };

  const handleItemAdded = () => {
    setCurrentScreen('wishlist');
  };

  const handleItemClick = (itemId) => {
    setSelectedItemId(itemId);
    setCurrentScreen('item');
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case 'main':
        return <MainScreen onWishlistClick={handleWishlistClick} onCreateWishlist={handleCreateWishlist} />;
      case 'wishlist':
        return <WishlistScreen wishlistId={selectedWishlistId} onBack={handleBack} onAddItem={handleAddItem} onItemClick={handleItemClick} />;
      case 'create-wishlist':
        return <CreateWishlistScreen onBack={handleBack} onWishlistCreated={handleWishlistCreated} />;
      case 'add-item':
        return <AddItemScreen wishlistId={selectedWishlistId} onBack={handleBack} onItemAdded={handleItemAdded} />;
      case 'item':
        return <ItemScreen itemId={selectedItemId} wishlistId={selectedWishlistId} onBack={handleBack} />;
      default:
        return <MainScreen onWishlistClick={handleWishlistClick} onCreateWishlist={handleCreateWishlist} />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          bgcolor: 'background.default',
          minHeight: '100vh',
          color: 'text.primary',
        }}
      >
        {renderScreen()}
      </Box>
    </ThemeProvider>
  );
}

export default App;