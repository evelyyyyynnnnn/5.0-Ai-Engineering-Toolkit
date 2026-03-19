//
//  DiscoverPageView.swift
//  BrewMeet
//
//  Created by Evelyn Du on 9/20/25.
//

import SwiftUI

struct DiscoverPageView: View {
    @Environment(\.horizontalSizeClass) var horizontalSizeClass
    @Environment(\.verticalSizeClass) var verticalSizeClass
    
    @State private var currentIndex = 0
    @State private var users = MockData.users
    @State private var showingFilters = false
    @State private var selectedFilters: [String] = []
    
    private let filterOptions = [
        "Coffee Type", "Distance", "Age Range", "Availability", 
        "Coffee Shop", "Interests", "Occupation", "Activity"
    ]
    
    var body: some View {
        GeometryReader { geometry in
            let isCompact = horizontalSizeClass == .compact
            
            VStack(spacing: 0) {
                // Header with filter button
                HStack {
                    Button(action: { showingFilters = true }) {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                            .font(.system(size: isCompact ? 20 : 24))
                            .foregroundColor(.black)
                    }
                    
                    Spacer()
                    
                    Button(action: resetCards) {
                        Image(systemName: "arrow.clockwise")
                            .font(.system(size: isCompact ? 20 : 24))
                            .foregroundColor(.black)
                    }
                }
                .padding(.horizontal, isCompact ? 16 : 32)
                .padding(.vertical, 12)
                .background(Color.white)
                
                // Filter bar
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) {
                        ForEach(filterOptions, id: \.self) { filter in
                            FilterChip(
                                title: filter,
                                isSelected: selectedFilters.contains(filter)
                            ) {
                                toggleFilter(filter)
                            }
                        }
                    }
                    .padding(.horizontal, isCompact ? 16 : 32)
                }
                .padding(.vertical, 8)
                .background(Color.white)
                
                // Content area: scrollable profile cards
                if currentIndex < users.count {
                    ScrollView(.vertical, showsIndicators: false) {
                        VStack(spacing: 16) {
                            // Main profile card
                            EnhancedProfileCard(
                                user: users[currentIndex],
                                onPass: handlePass,
                                onLike: handleLike
                            )
                            .frame(maxWidth: min(geometry.size.width - (isCompact ? 32 : 64), 400))
                            .padding(.horizontal, isCompact ? 16 : 32)
                            
                            // Additional profile details
                            ProfileDetailsCard(user: users[currentIndex])
                                .frame(maxWidth: min(geometry.size.width - (isCompact ? 32 : 64), 400))
                                .padding(.horizontal, isCompact ? 16 : 32)
                            
                            // Coffee preferences card
                            CoffeePreferencesCard(user: users[currentIndex])
                                .frame(maxWidth: min(geometry.size.width - (isCompact ? 32 : 64), 400))
                                .padding(.horizontal, isCompact ? 16 : 32)
                            
                            // Interests and topics card
                            InterestsCard(user: users[currentIndex])
                                .frame(maxWidth: min(geometry.size.width - (isCompact ? 32 : 64), 400))
                                .padding(.horizontal, isCompact ? 16 : 32)
                        }
                        .padding(.vertical, 16)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    // No more users message
                    VStack(spacing: isCompact ? 16 : 24) {
                        Image(systemName: "cup.and.saucer")
                            .font(.system(size: isCompact ? 60 : 80))
                            .foregroundColor(.gray)
                        
                        Text("No more coffee partners for now")
                            .font(.system(size: isCompact ? 18 : 22, weight: .medium))
                            .foregroundColor(.black)
                        
                        Text("Check back later or adjust your preferences")
                            .font(.system(size: isCompact ? 14 : 18))
                            .foregroundColor(.gray)
                            .multilineTextAlignment(.center)
                        
                        CustomButton("Start Over", style: .primary) {
                            resetCards()
                        }
                        .frame(width: isCompact ? 120 : 160)
                    }
                    .padding(isCompact ? 32 : 48)
                    .background(Color.white)
                    .cornerRadius(12)
                    .shadow(color: Color.black.opacity(0.1), radius: 2, x: 0, y: 1)
                    .padding(.horizontal, isCompact ? 24 : 40)
                    .frame(maxWidth: isCompact ? .infinity : 500)
                }
                
                // Progress indicator
                if currentIndex < users.count {
                    HStack(spacing: isCompact ? 8 : 12) {
                        ForEach(0..<users.count, id: \.self) { index in
                            Circle()
                                .fill(index <= currentIndex ? Color.black : Color.gray.opacity(0.3))
                                .frame(width: isCompact ? 8 : 10, height: isCompact ? 8 : 10)
                        }
                    }
                    .padding(.bottom, isCompact ? 20 : 30)
                }
            }
            .background(Color.gray.opacity(0.05))
        }
        .sheet(isPresented: $showingFilters) {
            FilterPageView(selectedFilters: $selectedFilters)
        }
    }
    
    // MARK: - Helper Functions
    private func toggleFilter(_ filter: String) {
        if selectedFilters.contains(filter) {
            selectedFilters.removeAll { $0 == filter }
        } else {
            selectedFilters.append(filter)
        }
    }
    
    // Handle pass action
    private func handlePass() {
        if currentIndex < users.count - 1 {
            currentIndex += 1
        } else {
            // If at the end, start from the beginning
            currentIndex = 0
        }
    }
    
    // Handle like action
    private func handleLike() {
        print("Liked \(users[currentIndex].name)")
        handlePass()
    }
    
    private func resetCards() {
        currentIndex = 0
    }
}

#Preview {
    DiscoverPageView()
}