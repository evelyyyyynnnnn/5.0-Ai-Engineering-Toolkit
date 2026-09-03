import { Heart, X, Coffee, MapPin, Briefcase } from "lucide-react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { ImageWithFallback } from './figma/ImageWithFallback';

interface ProfileCardProps {
  user: {
    id: string;
    name: string;
    age: number;
    photo: string;
    bio: string;
    interests: string[];
    occupation: string;
    location: string;
    coffeePreference: string;
  };
  onPass: () => void;
  onLike: () => void;
}

export function ProfileCard({ user, onPass, onLike }: ProfileCardProps) {
  return (
    <Card className="w-full max-w-sm mx-auto overflow-hidden bg-white shadow-lg">
      <div className="relative">
        <ImageWithFallback
          src={user.photo}
          alt={`${user.name}的照片`}
          className="w-full h-96 object-cover"
        />
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
          <h3 className="text-white mb-1">{user.name}, {user.age}</h3>
          <div className="flex items-center text-white/90 mb-2">
            <MapPin className="w-4 h-4 mr-1" />
            <span className="text-sm">{user.location}</span>
          </div>
        </div>
      </div>
      
      <div className="p-4 space-y-3">
        <div className="flex items-center text-muted-foreground">
          <Briefcase className="w-4 h-4 mr-2" />
          <span className="text-sm">{user.occupation}</span>
        </div>
        
        <div className="flex items-center text-muted-foreground">
          <Coffee className="w-4 h-4 mr-2" />
          <span className="text-sm">偏好: {user.coffeePreference}</span>
        </div>
        
        <p className="text-sm text-muted-foreground">{user.bio}</p>
        
        <div className="flex flex-wrap gap-2">
          {user.interests.slice(0, 3).map((interest, index) => (
            <Badge key={index} variant="secondary" className="text-xs">
              {interest}
            </Badge>
          ))}
        </div>
        
        <div className="flex gap-3 pt-2">
          <Button 
            variant="outline" 
            size="lg" 
            className="flex-1 border-2 hover:bg-muted"
            onClick={onPass}
          >
            <X className="w-5 h-5" />
          </Button>
          <Button 
            size="lg" 
            className="flex-1 bg-primary hover:bg-primary/90"
            onClick={onLike}
          >
            <Heart className="w-5 h-5 mr-2" />
            约咖啡
          </Button>
        </div>
      </div>
    </Card>
  );
}