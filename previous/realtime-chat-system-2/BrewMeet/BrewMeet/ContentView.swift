//
//  ContentView.swift
//  BrewMeet
//
//  Created by Evelyn Du on 9/20/25.
//

import SwiftUI

enum Page: String, CaseIterable {
    case discover = "discover"
    case standouts = "standouts"
    case invitations = "invitations"
    case matches = "matches"
    case profile = "profile"
}

struct ContentView: View {
    @State private var currentPage: Page = .discover
    
    var body: some View {
        VStack(spacing: 0) {
            // Main Content
            Group {
                switch currentPage {
                case .discover:
                    DiscoverPageView()
                case .standouts:
                    StandoutsPageView()
                case .invitations:
                    InvitationsPageView()
                case .matches:
                    MatchesPageView()
                case .profile:
                    ProfilePageView()
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            
            // Bottom Navigation
            VStack(spacing: 0) {
                Divider()
                    .background(Color.black)
                
                HStack(spacing: 0) {
                    // Discover - App Logo
                    Button(action: { currentPage = .discover }) {
                        VStack(spacing: 4) {
                            ZStack {
                                Circle()
                                    .fill(currentPage == .discover ? Color.white : Color.clear)
                                    .frame(width: 48, height: 48)
                                
                                Image("AppLogo")
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                                    .frame(width: 36, height: 36)
                                    .clipped()
                                    .foregroundColor(currentPage == .discover ? .black : .white)
                            }
                        }
                    }
                    .frame(maxWidth: .infinity)
                    
                    // Standouts - Star icon
                    Button(action: { currentPage = .standouts }) {
                        VStack(spacing: 4) {
                            Image(systemName: "star.fill")
                                .font(.system(size: 24))
                                .foregroundColor(currentPage == .standouts ? .black : .white)
                                .frame(width: 48, height: 48)
                                .background(
                                    Circle()
                                        .fill(currentPage == .standouts ? Color.white : Color.clear)
                                )
                        }
                    }
                    .frame(maxWidth: .infinity)
                    
                    // Invitations - Heart icon with badge
                    Button(action: { currentPage = .invitations }) {
                        VStack(spacing: 4) {
                            ZStack {
                                Image(systemName: "heart.fill")
                                    .font(.system(size: 24))
                                    .foregroundColor(currentPage == .invitations ? .black : .white)
                                    .frame(width: 48, height: 48)
                                    .background(
                                        Circle()
                                            .fill(currentPage == .invitations ? Color.white : Color.clear)
                                    )
                                
                                // Badge for new invitations
                                Circle()
                                    .fill(Color.red)
                                    .frame(width: 12, height: 12)
                                    .offset(x: 16, y: -16)
                            }
                        }
                    }
                    .frame(maxWidth: .infinity)
                    
                    // Matches - Chat icon with badge
                    Button(action: { currentPage = .matches }) {
                        VStack(spacing: 4) {
                            ZStack {
                                Image(systemName: "message.fill")
                                    .font(.system(size: 24))
                                    .foregroundColor(currentPage == .matches ? .black : .white)
                                    .frame(width: 48, height: 48)
                                    .background(
                                        Circle()
                                            .fill(currentPage == .matches ? Color.white : Color.clear)
                                    )
                                
                                // Badge with number
                                ZStack {
                                    Circle()
                                        .fill(Color.red)
                                        .frame(width: 20, height: 20)
                                    
                                    Text("3")
                                        .font(.system(size: 12, weight: .bold))
                                        .foregroundColor(.white)
                                }
                                .offset(x: 16, y: -16)
                            }
                        }
                    }
                    .frame(maxWidth: .infinity)
                    
                    // Profile - User avatar
                    Button(action: { currentPage = .profile }) {
                        VStack(spacing: 4) {
                            AsyncImage(url: URL(string: "https://images.unsplash.com/photo-1746114774895-133d5b677db8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBzaG9wJTIwY2FzdWFsJTIwcGVyc29ufGVufDF8fHx8MTc1ODM5MTYzMXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral")) { image in
                                image
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                            } placeholder: {
                                Circle()
                                    .fill(Color.gray.opacity(0.3))
                            }
                            .frame(width: 48, height: 48)
                            .clipShape(Circle())
                            .overlay(
                                Circle()
                                    .stroke(currentPage == .profile ? Color.white : Color.clear, lineWidth: 2)
                            )
                        }
                    }
                    .frame(maxWidth: .infinity)
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 8)
                .background(Color.black)
                
                // Home indicator like iPhone
                HStack {
                    Spacer()
                    RoundedRectangle(cornerRadius: 2)
                        .fill(Color.white)
                        .frame(width: 128, height: 4)
                    Spacer()
                }
                .padding(.bottom, 34) // 增加底部内边距以适应安全区域
            }
            .background(Color.black)
            .ignoresSafeArea(.all, edges: .bottom)
        }
        .background(Color.white)
    }
}

#Preview {
    ContentView()
}
