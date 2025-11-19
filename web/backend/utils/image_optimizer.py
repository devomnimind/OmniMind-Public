"""
Image optimization utilities for web delivery.

This module provides production-grade image optimization with:
- WebP conversion (superior compression)
- JPEG optimization
- PNG optimization  
- Automatic quality adjustment
- Resize support
- Metadata stripping

Example:
    >>> from web.backend.utils.image_optimizer import ImageOptimizer
    >>> optimizer = ImageOptimizer(default_quality=85)
    >>> webp_bytes = optimizer.to_webp(jpeg_bytes, quality=90)
"""

from typing import Tuple, Optional, Union
import io
import logging

# PIL is optional for local-first operation
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

logger = logging.getLogger(__name__)


class ImageOptimizer:
    """
    Optimizes images for web delivery.
    
    Supports WebP conversion, JPEG/PNG optimization, resizing,
    and metadata stripping for reduced file sizes.
    
    Attributes:
        default_quality: Default quality level (1-100)
        strip_metadata: Whether to remove EXIF/metadata
        
    Example:
        >>> optimizer = ImageOptimizer(default_quality=85)
        >>> webp = optimizer.to_webp(image_bytes)
        >>> jpeg = optimizer.optimize_jpeg(image_bytes, quality=90)
    """
    
    def __init__(
        self,
        default_quality: int = 85,
        strip_metadata: bool = True
    ):
        """
        Initialize image optimizer.
        
        Args:
            default_quality: Default quality 1-100 (default: 85)
            strip_metadata: Strip EXIF/metadata (default: True)
            
        Raises:
            ImportError: If PIL/Pillow not installed
        """
        if not PIL_AVAILABLE:
            logger.warning(
                "PIL/Pillow not available. "
                "Install with: pip install Pillow. "
                "Image optimization disabled."
            )
        
        self.default_quality = default_quality
        self.strip_metadata = strip_metadata
    
    def to_webp(
        self,
        image_bytes: bytes,
        quality: Optional[int] = None,
        resize: Optional[Tuple[int, int]] = None,
        lossless: bool = False
    ) -> bytes:
        """
        Convert image to WebP format.
        
        Args:
            image_bytes: Original image bytes
            quality: Quality 1-100 (optional, uses default)
            resize: Target size (width, height) (optional)
            lossless: Use lossless compression (default: False)
            
        Returns:
            WebP image bytes
            
        Example:
            >>> webp = optimizer.to_webp(
            ...     jpeg_bytes,
            ...     quality=90,
            ...     resize=(800, 600)
            ... )
        """
        if not PIL_AVAILABLE:
            logger.warning("PIL not available, returning original bytes")
            return image_bytes
        
        quality = quality or self.default_quality
        
        try:
            # Open image
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if img.mode in ("RGBA", "LA", "P"):
                # Preserve transparency for WebP
                pass
            elif img.mode != "RGB":
                img = img.convert("RGB")
            
            # Resize if requested
            if resize:
                img = img.resize(resize, Image.Resampling.LANCZOS)
            
            # Convert to WebP
            output = io.BytesIO()
            
            save_kwargs = {
                "format": "WEBP",
                "quality": quality,
                "method": 6  # Best compression (slowest)
            }
            
            if lossless:
                save_kwargs["lossless"] = True
                save_kwargs.pop("quality")
            
            img.save(output, **save_kwargs)
            
            webp_bytes = output.getvalue()
            
            reduction = 100 - (len(webp_bytes) / len(image_bytes) * 100)
            logger.info(
                f"WebP conversion: {len(image_bytes)} → {len(webp_bytes)} bytes "
                f"({reduction:.1f}% reduction)"
            )
            
            return webp_bytes
            
        except Exception as e:
            logger.error(f"WebP conversion failed: {e}")
            return image_bytes
    
    def optimize_jpeg(
        self,
        image_bytes: bytes,
        quality: Optional[int] = None,
        progressive: bool = True
    ) -> bytes:
        """
        Optimize JPEG image.
        
        Args:
            image_bytes: Original JPEG bytes
            quality: Quality 1-100 (optional)
            progressive: Use progressive encoding (default: True)
            
        Returns:
            Optimized JPEG bytes
            
        Example:
            >>> optimized = optimizer.optimize_jpeg(jpeg_bytes, quality=85)
        """
        if not PIL_AVAILABLE:
            return image_bytes
        
        quality = quality or self.default_quality
        
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            output = io.BytesIO()
            
            img.save(
                output,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=progressive
            )
            
            optimized_bytes = output.getvalue()
            
            reduction = 100 - (len(optimized_bytes) / len(image_bytes) * 100)
            logger.info(
                f"JPEG optimization: {len(image_bytes)} → {len(optimized_bytes)} bytes "
                f"({reduction:.1f}% reduction)"
            )
            
            return optimized_bytes
            
        except Exception as e:
            logger.error(f"JPEG optimization failed: {e}")
            return image_bytes
    
    def optimize_png(
        self,
        image_bytes: bytes,
        compress_level: int = 9
    ) -> bytes:
        """
        Optimize PNG image.
        
        Args:
            image_bytes: Original PNG bytes
            compress_level: Compression 0-9 (default: 9=best)
            
        Returns:
            Optimized PNG bytes
            
        Example:
            >>> optimized = optimizer.optimize_png(png_bytes)
        """
        if not PIL_AVAILABLE:
            return image_bytes
        
        try:
            img = Image.open(io.BytesIO(image_bytes))
            output = io.BytesIO()
            
            img.save(
                output,
                format="PNG",
                compress_level=compress_level,
                optimize=True
            )
            
            optimized_bytes = output.getvalue()
            
            reduction = 100 - (len(optimized_bytes) / len(image_bytes) * 100)
            logger.info(
                f"PNG optimization: {len(image_bytes)} → {len(optimized_bytes)} bytes "
                f"({reduction:.1f}% reduction)"
            )
            
            return optimized_bytes
            
        except Exception as e:
            logger.error(f"PNG optimization failed: {e}")
            return image_bytes
    
    def auto_optimize(
        self,
        image_bytes: bytes,
        target_format: Optional[str] = None,
        quality: Optional[int] = None
    ) -> Tuple[bytes, str]:
        """
        Automatically optimize image to best format.
        
        Args:
            image_bytes: Original image bytes
            target_format: Target format (webp/jpeg/png) or None for auto
            quality: Quality level (optional)
            
        Returns:
            Tuple of (optimized_bytes, format_used)
            
        Example:
            >>> optimized, format = optimizer.auto_optimize(image_bytes)
            >>> print(f"Optimized to {format}")
        """
        if not PIL_AVAILABLE:
            return image_bytes, "original"
        
        try:
            img = Image.open(io.BytesIO(image_bytes))
            original_format = img.format.lower() if img.format else "unknown"
            
            # Auto-detect best format
            if target_format is None:
                # WebP for most cases (best compression)
                if img.mode in ("RGB", "RGBA"):
                    target_format = "webp"
                # PNG for images with transparency or palettes
                elif img.mode in ("P", "LA"):
                    target_format = "png"
                else:
                    target_format = "jpeg"
            
            # Optimize based on target format
            if target_format == "webp":
                optimized = self.to_webp(image_bytes, quality=quality)
            elif target_format == "jpeg":
                optimized = self.optimize_jpeg(image_bytes, quality=quality)
            elif target_format == "png":
                optimized = self.optimize_png(image_bytes)
            else:
                logger.warning(f"Unknown format {target_format}, using original")
                optimized = image_bytes
                target_format = original_format
            
            return optimized, target_format
            
        except Exception as e:
            logger.error(f"Auto-optimization failed: {e}")
            return image_bytes, "original"
    
    def get_image_info(self, image_bytes: bytes) -> dict:
        """
        Get image information.
        
        Args:
            image_bytes: Image bytes
            
        Returns:
            Dict with width, height, format, mode, size
            
        Example:
            >>> info = optimizer.get_image_info(image_bytes)
            >>> print(f"{info['width']}x{info['height']} {info['format']}")
        """
        if not PIL_AVAILABLE:
            return {
                "error": "PIL not available",
                "size_bytes": len(image_bytes)
            }
        
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "size_bytes": len(image_bytes)
            }
            
        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            return {
                "error": str(e),
                "size_bytes": len(image_bytes)
            }
