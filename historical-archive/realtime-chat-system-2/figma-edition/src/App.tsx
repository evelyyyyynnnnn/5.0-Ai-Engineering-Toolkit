import { useState } from "react";
import { DiscoverPage } from "./components/DiscoverPage";
import { ProfilePage } from "./components/ProfilePage";
import { StandoutsPage } from "./components/StandoutsPage";
import { InvitationsPage } from "./components/InvitationsPage";
import { MatchesPage } from "./components/MatchesPage";
import { SettingsPage } from "./components/SettingsPage";
import { Button } from "./components/ui/button";
import { ImageWithFallback } from './components/figma/ImageWithFallback';
import { Star, Heart, Coffee, MessageCircle } from "lucide-react";

type Page = 'discover' | 'standouts' | 'invitations' | 'matches' | 'profile' | 'settings';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('discover');

  const handleChatClick = (chatId: string) => {
    // 这里可以导航到具体的聊天页面
    console.log(`Opening chat with ID: ${chatId}`);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'discover':
        return <DiscoverPage onSettingsClick={() => setCurrentPage('settings')} />;
      case 'standouts':
        return <StandoutsPage />;
      case 'invitations':
        return <InvitationsPage />;
      case 'matches':
        return <MatchesPage onChatClick={handleChatClick} />;
      case 'profile':
        return <ProfilePage onEditClick={() => console.log('Edit profile')} />;
      case 'settings':
        return <SettingsPage onBackClick={() => setCurrentPage('discover')} />;
      default:
        return <DiscoverPage onSettingsClick={() => setCurrentPage('settings')} />;
    }
  };

  if (currentPage === 'settings') {
    return renderPage();
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        {renderPage()}
      </div>

      {/* Bottom Navigation - 5 buttons exactly like Hinge */}
      <div className="border-t bg-black p-2">
        <div className="flex justify-around items-center max-w-md mx-auto">
          {/* Discover - H icon like Hinge */}
          <Button
            variant="ghost"
            size="icon"
            className={`w-12 h-12 rounded-full ${
              currentPage === 'discover' 
                ? 'bg-white text-black' 
                : 'text-white hover:bg-gray-800'
            }`}
            onClick={() => setCurrentPage('discover')}
          >
            <div className="text-xl font-bold">H</div>
          </Button>
          
          {/* Standouts - Star icon */}
          <Button
            variant="ghost"
            size="icon"
            className={`w-12 h-12 rounded-full ${
              currentPage === 'standouts' 
                ? 'bg-white text-black' 
                : 'text-white hover:bg-gray-800'
            }`}
            onClick={() => setCurrentPage('standouts')}
          >
            <Star className="w-6 h-6" />
          </Button>
          
          {/* Invitations - Heart icon */}
          <Button
            variant="ghost"
            size="icon"
            className={`w-12 h-12 rounded-full relative ${
              currentPage === 'invitations' 
                ? 'bg-white text-black' 
                : 'text-white hover:bg-gray-800'
            }`}
            onClick={() => setCurrentPage('invitations')}
          >
            <Heart className="w-6 h-6" />
            {/* Badge for new invitations */}
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
          </Button>
          
          {/* Matches - Chat icon with badge */}
          <Button
            variant="ghost"
            size="icon"
            className={`w-12 h-12 rounded-full relative ${
              currentPage === 'matches' 
                ? 'bg-white text-black' 
                : 'text-white hover:bg-gray-800'
            }`}
            onClick={() => setCurrentPage('matches')}
          >
            <MessageCircle className="w-6 h-6" />
            {/* Badge with number */}
            <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
              <span className="text-xs text-white">3</span>
            </div>
          </Button>
          
          {/* Profile - User avatar */}
          <Button
            variant="ghost"
            size="icon"
            className={`w-12 h-12 rounded-full p-0 overflow-hidden ${
              currentPage === 'profile' 
                ? 'ring-2 ring-white' 
                : 'hover:ring-2 hover:ring-gray-600'
            }`}
            onClick={() => setCurrentPage('profile')}
          >
            <ImageWithFallback
              src="https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
              alt="Your profile"
              className="w-full h-full object-cover"
            />
          </Button>
        </div>
        
        {/* Home indicator like iPhone */}
        <div className="flex justify-center mt-2">
          <div className="w-32 h-1 bg-white rounded-full"></div>
        </div>
      </div>
    </div>
  );
}