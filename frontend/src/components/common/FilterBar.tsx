import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Chip,
  SelectChangeEvent,
} from '@mui/material';
import { Category } from '../../types';

interface FilterBarProps {
  categories: Category[];
  selectedCategory: string;
  sortBy: string;
  onCategoryChange: (category: string) => void;
  onSortChange: (sort: string) => void;
}

const FilterBar: React.FC<FilterBarProps> = ({
  categories,
  selectedCategory,
  sortBy,
  onCategoryChange,
  onSortChange,
}) => {
  return (
    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel>Category</InputLabel>
        <Select
          value={selectedCategory}
          label="Category"
          onChange={(e: SelectChangeEvent) => onCategoryChange(e.target.value)}
        >
          <MenuItem value="">All Categories</MenuItem>
          {categories.map((cat) => (
            <MenuItem key={cat.id} value={String(cat.id)}>
              {cat.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <FormControl size="small" sx={{ minWidth: 150 }}>
        <InputLabel>Sort By</InputLabel>
        <Select
          value={sortBy}
          label="Sort By"
          onChange={(e: SelectChangeEvent) => onSortChange(e.target.value)}
        >
          <MenuItem value="">Default</MenuItem>
          <MenuItem value="price_low">Price: Low to High</MenuItem>
          <MenuItem value="price_high">Price: High to Low</MenuItem>
          <MenuItem value="name_asc">Name: A-Z</MenuItem>
          <MenuItem value="name_desc">Name: Z-A</MenuItem>
        </Select>
      </FormControl>

      {selectedCategory && (
        <Chip
          label={`Category: ${categories.find((c) => String(c.id) === selectedCategory)?.name}`}
          onDelete={() => onCategoryChange('')}
          size="small"
        />
      )}
    </Box>
  );
};

export default FilterBar;
