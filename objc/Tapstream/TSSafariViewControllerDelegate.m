//
//  TSSafariViewControllerDelegate.m
//  ExampleApp
//
//  Created by Adam Bard on 2015-09-12.
//  Copyright © 2015 Example. All rights reserved.
//

#import "TSSafariViewControllerDelegate.h"
#import "TSLogging.h"

@implementation TSSafariViewControllerDelegate

+ (void)presentSafariViewControllerWithURLAndCompletion:(NSURL*)url completion:(void (^)(void))completion
{
	Class safControllerClass = NSClassFromString(@"SFSafariViewController");
	if(safControllerClass != nil){
		id inst = [safControllerClass alloc];
		SEL sel = NSSelectorFromString(@"initWithURL:");
		IMP imp = [inst methodForSelector:sel];
		UIViewController* safController = ((id (*)(id, SEL, NSURL *))imp)(inst, sel, url);

		if(safController != nil){
			TSSafariViewControllerDelegate* me = [[TSSafariViewControllerDelegate alloc] init];

			me.completion = completion;

			me.hiddenWindow = [[UIWindow alloc] initWithFrame:CGRectZero];
			me.hiddenWindow.rootViewController = me;
			me.hiddenWindow.hidden = true;

			me.view.hidden = YES;
			me.modalPresentationStyle = UIModalPresentationOverFullScreen;

			sel = NSSelectorFromString(@"setDelegate:");
			imp = [safController methodForSelector:sel];
			((void (*)(id, SEL, id))imp)(safController, sel, me);

			[me.hiddenWindow makeKeyAndVisible];
			[me presentViewController:safController animated:YES completion:nil];
		}
	}else{
		[TSLogging logAtLevel:kTSLoggingWarn format:@"Tapstream could not load SFSafariViewController, is Safari Services framework enabled?"];
	}
}

- (void)dismiss
{
	[self.hiddenWindow.rootViewController dismissViewControllerAnimated:NO completion:self.completion];
}

// SFSafariViewController delegate methods
- (NSArray<UIActivity *> *)safariViewController:(id)controller activityItemsForURL:(NSURL *)URL title:(nullable NSString *)title
{
	return nil;
}

- (void)safariViewControllerDidFinish:(id)controller
{
}

- (void)safariViewController:(id)controller didCompleteInitialLoad:(BOOL)didLoadSuccessfully
{
	[controller dismissViewControllerAnimated:false completion:^{
		[self dismiss];
	}];
}

@end