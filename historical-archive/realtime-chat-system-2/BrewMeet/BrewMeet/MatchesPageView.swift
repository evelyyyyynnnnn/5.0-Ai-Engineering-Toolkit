//
//  MatchesPageView.swift
//  BrewMeet
//
//  Created by Evelyn Du on 9/20/25.
//

import SwiftUI

struct MatchesPageView: View {
    @State private var selectedTab = 0
    private let matches = MockData.matches
    
    private var newMatches: [Match] {
        matches.filter { $0.status == .newMatch }
    }
    
    private var conversations: [Match] {
        matches.filter { $0.status != .newMatch }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                HStack(spacing: 8) {
                    Image(systemName: "heart.fill")
                        .font(.system(size: 20))
                        .foregroundColor(.pink)
                    Text("Matches")
                        .font(.system(size: 20, weight: .bold))
                        .foregroundColor(.black)
                }
                
                Spacer()
                
                if !newMatches.isEmpty {
                    Badge("\(newMatches.count) New", color: .error)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(Color.white)
            
            // Tabs
            HStack(spacing: 0) {
                TabButton(title: "All", isSelected: selectedTab == 0) {
                    selectedTab = 0
                }
                TabButton(title: "New", isSelected: selectedTab == 1) {
                    selectedTab = 1
                }
                TabButton(title: "Chats", isSelected: selectedTab == 2) {
                    selectedTab = 2
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(Color.white)
            
            Divider()
            
            // Content
            ScrollView {
                VStack(spacing: 16) {
                    if selectedTab == 0 {
                        AllMatchesView(matches: matches, newMatches: newMatches, conversations: conversations)
                    } else if selectedTab == 1 {
                        NewMatchesView(matches: newMatches)
                    } else {
                        ConversationsView(matches: conversations)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 16)
            }
        }
        .background(Color.gray.opacity(0.05))
    }
}

struct TabButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(isSelected ? .black : .gray)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
                .overlay(
                    Rectangle()
                        .fill(isSelected ? Color.black : Color.clear)
                        .frame(height: 2)
                        .offset(y: 16)
                )
        }
    }
}

struct AllMatchesView: View {
    let matches: [Match]
    let newMatches: [Match]
    let conversations: [Match]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            if matches.isEmpty {
                EmptyMatchesView()
            } else {
                // New Matches Section
                if !newMatches.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: "heart.fill")
                                .font(.system(size: 16))
                                .foregroundColor(.pink)
                            Text("New Matches (\(newMatches.count))")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.black)
                        }
                        
                        LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 3), spacing: 12) {
                            ForEach(newMatches) { match in
                                NewMatchCard(match: match)
                            }
                        }
                    }
                }
                
                // Conversations Section
                if !conversations.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: "message.fill")
                                .font(.system(size: 16))
                                .foregroundColor(.blue)
                            Text("Conversations (\(conversations.count))")
                                .font(.system(size: 16, weight: .bold))
                                .foregroundColor(.black)
                        }
                        
                        VStack(spacing: 12) {
                            ForEach(conversations) { match in
                                ConversationCard(match: match)
                            }
                        }
                    }
                }
            }
        }
    }
}

struct NewMatchesView: View {
    let matches: [Match]
    
    var body: some View {
        if matches.isEmpty {
            EmptyNewMatchesView()
        } else {
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 16) {
                ForEach(matches) { match in
                    NewMatchCard(match: match)
                }
            }
        }
    }
}

struct ConversationsView: View {
    let matches: [Match]
    
    var body: some View {
        if matches.isEmpty {
            EmptyConversationsView()
        } else {
            VStack(spacing: 12) {
                ForEach(matches) { match in
                    ConversationCard(match: match)
                }
            }
        }
    }
}

struct NewMatchCard: View {
    let match: Match
    
    var body: some View {
        VStack(spacing: 12) {
            AsyncImageWithFallback(
                url: match.photo,
                contentMode: .fill
            )
            .frame(width: 80, height: 80)
            .clipShape(Circle())
            
            VStack(spacing: 4) {
                Text("\(match.name), \(match.age)")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.black)
                
                HStack {
                    Image(systemName: "location.fill")
                        .font(.system(size: 12))
                        .foregroundColor(.gray)
                    Text(match.location)
                        .font(.system(size: 12))
                        .foregroundColor(.gray)
                }
                
                Badge(match.matchedOn + " ago", color: .pink)
                
                CustomButton("Start Chat", style: .primary, size: .small) {
                    // Handle chat action
                }
            }
        }
        .padding(12)
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: 1)
    }
}

struct ConversationCard: View {
    let match: Match
    
    var body: some View {
        HStack(spacing: 12) {
            ZStack(alignment: .topTrailing) {
                AsyncImageWithFallback(
                    url: match.photo,
                    contentMode: .fill
                )
                .frame(width: 56, height: 56)
                .clipShape(Circle())
                
                if match.unread {
                    Circle()
                        .fill(Color.blue)
                        .frame(width: 12, height: 12)
                        .offset(x: 4, y: -4)
                }
            }
            
            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text("\(match.name), \(match.age)")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.black)
                    
                    Badge(match.status.displayName, color: getBadgeColor(for: match.status))
                    
                    Spacer()
                    
                    Text(match.timestamp)
                        .font(.system(size: 12))
                        .foregroundColor(.gray)
                }
                
                HStack {
                    Image(systemName: "location.fill")
                        .font(.system(size: 12))
                        .foregroundColor(.gray)
                    Text(match.location)
                        .font(.system(size: 12))
                        .foregroundColor(.gray)
                    Text("•")
                        .font(.system(size: 12))
                        .foregroundColor(.gray)
                    Text(match.matchedOn + " ago")
                        .font(.system(size: 12))
                        .foregroundColor(.gray)
                }
                
                if let lastMessage = match.lastMessage {
                    Text(lastMessage)
                        .font(.system(size: 14))
                        .foregroundColor(match.unread ? .black : .gray)
                        .lineLimit(1)
                }
            }
            
            Image(systemName: getStatusIcon(for: match.status))
                .font(.system(size: 16))
                .foregroundColor(getStatusColor(for: match.status))
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: 1)
    }
    
    private func getBadgeColor(for status: MatchStatus) -> Badge.BadgeColor {
        switch status {
        case .newMatch: return .pink
        case .chatting: return .blue
        case .planning: return .orange
        case .scheduled: return .green
        }
    }
    
    private func getStatusIcon(for status: MatchStatus) -> String {
        switch status {
        case .newMatch: return "heart.fill"
        case .chatting: return "message.fill"
        case .planning: return "cup.and.saucer.fill"
        case .scheduled: return "calendar.fill"
        }
    }
    
    private func getStatusColor(for status: MatchStatus) -> Color {
        switch status {
        case .newMatch: return .pink
        case .chatting: return .blue
        case .planning: return .orange
        case .scheduled: return .green
        }
    }
}

struct EmptyMatchesView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "heart")
                .font(.system(size: 64))
                .foregroundColor(.gray)
            
            Text("No matches yet")
                .font(.system(size: 18, weight: .medium))
                .foregroundColor(.black)
            
            Text("Start browsing and liking other users to get matches!")
                .font(.system(size: 14))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
        }
        .padding(32)
    }
}

struct EmptyNewMatchesView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "heart")
                .font(.system(size: 64))
                .foregroundColor(.gray)
            
            Text("No new matches")
                .font(.system(size: 18, weight: .medium))
                .foregroundColor(.black)
            
            Text("Keep browsing to get more matches!")
                .font(.system(size: 14))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
        }
        .padding(32)
    }
}

struct EmptyConversationsView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "message")
                .font(.system(size: 64))
                .foregroundColor(.gray)
            
            Text("No conversations yet")
                .font(.system(size: 18, weight: .medium))
                .foregroundColor(.black)
            
            Text("Start chatting with your matches and plan a coffee meetup!")
                .font(.system(size: 14))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
        }
        .padding(32)
    }
}

#Preview {
    MatchesPageView()
}
