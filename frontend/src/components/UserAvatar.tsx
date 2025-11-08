import React from 'react'

interface UserAvatarProps {
  firstName?: string
  lastName?: string
  username?: string
  size?: 'sm' | 'md' | 'lg'
  photoUrl?: string
}

export const UserAvatar: React.FC<UserAvatarProps> = ({ 
  firstName, 
  lastName, 
  username,
  size = 'md',
  photoUrl 
}) => {
  const getInitials = () => {
    if (firstName && lastName) {
      return `${firstName[0]}${lastName[0]}`.toUpperCase()
    }
    if (firstName) {
      return firstName[0].toUpperCase()
    }
    if (username) {
      return username[0].toUpperCase()
    }
    return '?'
  }

  const sizeClasses = {
    sm: 'w-10 h-10 text-sm',
    md: 'w-12 h-12 text-base',
    lg: 'w-16 h-16 text-xl'
  }

  const getGradientColor = () => {
    // Generate consistent color based on user info
    const str = firstName || lastName || username || 'default'
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash)
    }
    
    const gradients = [
      'from-blue-400 to-blue-600',
      'from-purple-400 to-purple-600',
      'from-pink-400 to-pink-600',
      'from-indigo-400 to-indigo-600',
      'from-cyan-400 to-cyan-600',
      'from-teal-400 to-teal-600',
      'from-green-400 to-green-600',
      'from-orange-400 to-orange-600',
    ]
    
    return gradients[Math.abs(hash) % gradients.length]
  }

  if (photoUrl) {
    return (
      <div className={`${sizeClasses[size]} rounded-full overflow-hidden flex-shrink-0 ring-2 ring-white/20`}>
        <img 
          src={photoUrl} 
          alt={firstName || username || 'User'} 
          className="w-full h-full object-cover"
        />
      </div>
    )
  }

  return (
    <div 
      className={`${sizeClasses[size]} rounded-full flex items-center justify-center font-semibold text-white bg-gradient-to-br ${getGradientColor()} flex-shrink-0 ring-2 ring-white/20 shadow-lg`}
    >
      {getInitials()}
    </div>
  )
}
